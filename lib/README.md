# Prisma Cloud Alert report 

Version: *1.0*
Author: *Eddie Beuerlein*

### Summary
This script generates a high level email report based on alert data in the Prisma Cloud tenant

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

### Configuration

1. Navigate to *config/configs.yml*

2. Fill out your Prisma Cloud access key/secret, and stack info. To determine stack, look at your browser when access console (appX.prismacloud.io, where X is the stack number)  
Change this to apiX.prismacloud.io and populate it in the configs.yml.

### Run

```
python runner.py

```