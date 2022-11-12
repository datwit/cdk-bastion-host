#!/bin/sh
###################################################################
#Script Name: mapdbs
#Description: Create SSH tunnels using a bastion host
#Args: ssh key path
#Author: Yoel Benítez Fonseca
#Email: ybenitezf@datwit.com
###################################################################

if [ -z $1 ]; then
    echo "Usage: $0 path_to_private_ssh_key"
    echo "Example: $0 ~/.ssh/id_rsa"
    exit 1
fi

INSTANCE_DESC=$(aws ec2 describe-instances --no-cli-pager \
    --filter "Name=tag:Name,Values=secure-bastion" \
    --query "Reservations[].Instances[?State.Name =='running']" \
    --output json)

INSTANCE_ID=$(echo "$INSTANCE_DESC" | jq -r .[0][0].InstanceId)
PUBLIC_DNS_NAME=$(echo "$INSTANCE_DESC" | jq -r .[0][0].PublicDnsName)
AVAILABILITY_ZONE=$(echo "$INSTANCE_DESC" | jq -r .[0][0].Placement.AvailabilityZone)

echo "Bastion InstanceId: $INSTANCE_ID"
echo "Bastion DNS Name: $PUBLIC_DNS_NAME"
echo "Bastion VPC Availability Zone: $AVAILABILITY_ZONE"
aws ec2-instance-connect send-ssh-public-key \
    --region us-east-1 --instance-id $INSTANCE_ID \
    --availability-zone $AVAILABILITY_ZONE --instance-os-user ec2-user \
    --ssh-public-key file://$1.pub

NEPTUNEDB_DESC=$(aws neptune describe-db-clusters --no-cli-pager \
    --filters "Name=engine,Values=neptune" \
    --query "DBClusters[?contains(DBClusterIdentifier, 'neptunedatabase') == \`true\`]")

NEPTUNE_END_POINT=$(echo "$NEPTUNEDB_DESC" | jq -r .[0].Endpoint)
NEPTUNE_END_PORT=$(echo "$NEPTUNEDB_DESC" | jq -r .[0].Port)


echo "Mounting tunnel for $NEPTUNE_END_POINT in 127.0.0.1:$NEPTUNE_END_PORT"
echo "   "
echo "Remember to add $NEPTUNE_END_POINT to /etc/hosts with 127.0.0.1"
echo "to avoid SSL connections issue with AWS Neptune"
ssh -o StrictHostKeyChecking=accept-new -o ExitOnForwardFailure=yes \
    -f -N ec2-user@$PUBLIC_DNS_NAME -i $1 \
    -L 8182:$NEPTUNE_END_POINT:$NEPTUNE_END_PORT

echo "   "
echo "To login to Bastion Host use:"
echo "ssh -i $1 ec2-user@$PUBLIC_DNS_NAME"
echo "   "
echo "For tunnels run:"
echo "ssh -i $1 ec2-user@$PUBLIC_DNS_NAME -L LOCAL_PORT:ENDPOINT:REMOTE_PORT"