#Prisma Cloud Alert report email

Version: *1.0*
Author: *Eddie Beuerlein*

### Summary
Script pulls tenant and account level details on new and high risk counts for alerts, as well as top 5 policies in violation (including count) and sends in email report.

### Requirements and Dependencies

1. Python 3.7 or newer

2. OpenSSL 1.0.2 or newer

(if using on Mac OS, additional items may be nessessary.)

3. Pip

```sudo easy_install pip```

4. Requests (Python library)

```sudo pip install requests```

5. YAML (Python library)

```sudo pip install pyyaml```

6. Email (Python library)
```sudo pip install email.mime```
```sudo pip install smtplib```

### Configuration

1. Navigate to *config/configs.yml*

2. Fill out your Prisma Cloud access key/secret, and stack info. To determine stack, look at your browser when access console (appX.prismacloud.io, where X is the stack number.  Change this to apiX.prismacloud.io and populate it in the configs.yml.

3. Navigate to *lib/email_helper.py:
* Set from address: self.from_address = "XXXX@gmail.com"
* Set to address: self.to_address = "XXXXX@gmail.com"
* Set mail server: self.email_srv = "smtp.gmail.com"
* Set mail server port: self.email_srv_port = "587"
* Set mail login usernname: self.username = "XXXXXXX@gmail.com"
* Set mail login password: self.password = "XYZABC123"

### Run

```
python runner.py

```
