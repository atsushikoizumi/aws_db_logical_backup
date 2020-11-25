import json
import os

os.environ['tags_owner']="koizumi"
os.environ['tags_env']="dev"
os.environ['PASSWORD_KEY']="oracle"
se_nm = os.environ['tags_owner'] + "-" + os.environ['tags_env'] + "_DBPASSWORD"
f = open('sample.json', 'r')
os.environ["{}".format(se_nm)]=f.read()
ps = json.loads(os.environ["{}".format(se_nm)])
pwd = ps[os.environ['PASSWORD_KEY']]

print(pwd)

