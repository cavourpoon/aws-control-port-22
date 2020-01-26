import json
import boto3

def readConfig():
    f = open("config.json", "r")
    config=json.loads(f.read())
    region=input("Which region are you going to check? (HK=1, SG=2): ")
    if region=="1":
        return config['HK']
    elif region=="2":
        return config['SG']
    else:
        raise Exception("You have not select any valid region.")

def main():
    try:
        config=readConfig()
        sg_id=config['sg_id']
        vpc_region=config['region']
        client = boto3.client('ec2', region_name=vpc_region)
        response = client.describe_security_groups(
            GroupIds=[sg_id],
            DryRun=False,
        )
        print('Now checking security group ('+ sg_id +') configurations in '+ vpc_region)
        rules = response['SecurityGroups'][0]['IpPermissions']
        sshPortOpen=False
        for rule in rules:
            print("Port "+str(rule['ToPort'])+" is opening.")
            if rule['ToPort'] == 22:
                sshPortOpen=True

        if sshPortOpen:
            removeSshRule(sg_id,vpc_region)
        else:
            addSshRule(sg_id,vpc_region)
    except Exception as e:
        print(str(e))

def addSshRule(sg_id,vpc_region):
    print('Port 22 is closed. Now we are opening it now.')
    client = boto3.client('ec2', region_name=vpc_region)
    response = client.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[
            {
                'FromPort':22,
                'ToPort': 22,
                'IpProtocol': 'TCP',
                'IpRanges': [
                    {
                        'CidrIp': '0.0.0.0/0',
                        'Description': 'Ipv4 SSH'
                    },
                ],
            }
        ],
        DryRun=False
    )
    if response:
        print('Port 22 is opening now.')

def removeSshRule(sg_id,vpc_region):
    print('Port 22 is opening. Now we are closing it now.')
    client = boto3.client('ec2', region_name=vpc_region)
    response = client.revoke_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[
            {
                'FromPort':22,
                'ToPort': 22,
                'IpProtocol': 'TCP',
                'IpRanges': [
                    {
                        'CidrIp': '0.0.0.0/0',
                        'Description': 'Ipv4 SSH'
                    },
                ],
            }
        ],
        DryRun=False
    )
    if response:
        print('Port 22 is closed now.')

main()
