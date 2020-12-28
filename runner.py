import lib
import sys
from collections import defaultdict


class PCAlertEmailReport():
    def __init__(self):
        self.config = lib.ConfigHelper()
        self.pc_sess = lib.PCSession(self.config.pc_user, self.config.pc_pass, self.config.pc_cust,
                                     self.config.pc_api_base)
        self.email_send = lib.EmailHelper()
        if self.config.pc_user is None:
            print("No access key specified, please fix and re-run script")
            sys.exit()
        if self.config.pc_pass is None:
            print("No secret key specified, please fix and re-run script")
            sys.exit()


    def map_callback(self):
        if self.config.pc_api_base == "api.prismacloud.io":
            callback_base = "app.prismacloud.io"
        elif self.config.pc_api_base == "api2.prismacloud.io":
            callback_base = "app2.prismacloud.io"
        elif self.config.pc_api_base == "api3.prismacloud.io":
            callback_base = "app3.prismacloud.io"

        return callback_base

    def build_email_list(self):
        #data structure - {email address: [ acct id1, acct id2, acct id3] }
        email_list = defaultdict(list)
        self.pc_sess.authenticate_client()

        #collect all roles
        self.url = "https://" + self.config.pc_api_base + "/user/role"
        roles = self.pc_sess.client.get(self.url)

        #collect account groups
        self.url = "https://" + self.config.pc_api_base + "/cloud/group"
        acct_grps = self.pc_sess.client.get(self.url)

        # pull list of active accounts
        self.url = "https://" + self.config.pc_api_base + "/cloud/name?onlyActive=true"
        activeaccts = self.pc_sess.client.get(self.url)

        allacctids = []
        for acct in activeaccts.json():
            allacctids.append(acct['id'])

        for role in roles.json():
            if role['roleType'] == "Build and Deploy Security":
                continue
            elif role['roleType'] != "System Admin":
                for email in role['associatedUsers']:
                    if email in email_list.keys():
                        for acct in role['accountGroupIds']:
                            for target in acct_grps.json():
                                if target['id'] == acct:
                                    if target['accountIds']:
                                        email_list[email].extend(target['accountIds'])
                    else:
                        for acct in role['accountGroupIds']:
                            for target in acct_grps.json():
                                if target['id'] == acct:
                                    if target['accountIds']:
                                        email_list[email] = target['accountIds']
            else:
                for email in role['associatedUsers']:
                    if email in email_list.keys():
                        email_list[email].extend(allacctids)
                    else:
                        email_list[email].extend(allacctids)

        # post-processing - de-dup values
        for key,value in email_list.items():
            email_list[key] = list(set(value))


        return email_list

    def gather_toplevel(self):

        topinfo = {}
        self.pc_sess.authenticate_client()

        #pull last 24 hrs open alerts
        self.url = "https://" + self.config.pc_api_base + "/v2/alert?timeType=relative&timeAmount=24&timeUnit=hour" \
                   "&detailed=false&fields=alert.status&alert.status=open"

        top_new_open = self.pc_sess.client.get(self.url)
        topinfo['top_new_open'] = top_new_open.json()['totalRows']

        #pull last 24 hrs open high alerts
        self.url = "https://" + self.config.pc_api_base + "/v2/alert?timeType=relative&timeAmount=24&timeUnit=hour" \
                   "&detailed=false&fields=alert.status&alert.status=open&policy.severity=high"

        top_new_high = self.pc_sess.client.get(self.url)
        topinfo['top_new_high'] = top_new_high.json()['totalRows']

        #pull total number of alerts in tenant
        self.url = "https://" + self.config.pc_api_base + "/alert/count/open"

        top_total = self.pc_sess.client.get(self.url)
        topinfo['top_total'] = top_total.json()["count"]

        return topinfo

    def gather_acctlevel(self):
        acctinfo = defaultdict(dict)
        self.pc_sess.authenticate_client()

        #pull list of active accounts
        self.url = "https://" + self.config.pc_api_base + "/cloud/name?onlyActive=true"
        activeaccts = self.pc_sess.client.get(self.url)

        # iterate over cloud accounts (in json format)
        for acct in activeaccts.json():

            # pull last 24 hrs open alerts
            self.url = "https://" + self.config.pc_api_base + "/v2/alert?timeType=relative&timeAmount=24&timeUnit=hour" \
                                                          "&detailed=false&fields=alert.status&alert.status=open" \
                                                          "&cloud.accountId=" + acct["id"]

            top_new_open = self.pc_sess.client.get(self.url)
            acctinfo[acct['id']]['top_new_open'] = top_new_open.json()['totalRows']

            # pull last 24 hrs open high alerts
            self.url = "https://" + self.config.pc_api_base + "/v2/alert?timeType=relative&timeAmount=24&timeUnit=hour" \
                                                         "&detailed=false&fields=alert.status&alert.status=open" \
                                                         "&policy.severity=high&cloud.accountId=" + acct["id"]

            top_new_high = self.pc_sess.client.get(self.url)
            acctinfo[acct['id']]['top_new_high'] = top_new_high.json()['totalRows']

            # pull total number of alerts in tenant
            self.url = "https://" + self.config.pc_api_base + "/v2/alert?&timeType=to_now&timeUnit=epoch" \
                                                          "&detailed=false&alert.status=open" \
                                                          "&fields=alert.status&cloud.accountId=" + acct["id"]

            top_total = self.pc_sess.client.get(self.url)
            acctinfo[acct['id']]['top_total'] = top_total.json()['totalRows']

        return acctinfo

    def gather_top_risks(self):
        toprisk = {}
        self.pc_sess.authenticate_client()

        self.url = "https://" + self.config.pc_api_base + "/alert/policy?timeType=to_now&timeUnit=epoch" \
                                                          "&detailed=false&alert.status=open"
        policies = self.pc_sess.client.get(self.url)
        for policy in policies.json():
            toprisk[policy['policy']['name']] = policy['alertCount']

        return toprisk


    def build_email(self, toplevel, acctlevel, summarylevel, callback_base, email_addr):
        top = toplevel
        accts = acctlevel
        risks = summarylevel

        callback_url_top_new_open = \
            "https://" + callback_base + "/alerts/overview#alert.status=open&timeAmount=24" \
                                         "&timeType=relative&timeUnit=hour"
        callback_url_top_new_high = \
            "https://" + callback_base + "/alerts/overview#alert.status=open&policy.severity=high" \
                                         "&timeAmount=24&timeType=relative&timeUnit=hour"
        callback_url_top_total = \
            "https://" + callback_base + "/alerts/overview#alert.status=open&timeType=to_now&timeUnit=epoch"

        body = f"Daily Risk Summary\n\nNew risks identified: {top['top_new_open']} ({callback_url_top_new_open})\n" \
               f"New high risk alerts: {top['top_new_high']} ({callback_url_top_new_high})\n" \
               f"Total risks identified: {top['top_total']} ({callback_url_top_total})\n\n"

        for acct,acct_data in accts.items():
            if ((acct_data['top_new_open'] == 0) and (acct_data['top_new_high'] == 0)):
                continue
            else:
                callback_url_acct_top_new_open = "https://" + callback_base + "/alerts/overview#alert.status=open" \
                                                                          "&timeAmount=24&timeType=relative" \
                                                                          "&timeUnit=hour&cloud.accountId={}".format(acct)

                body2 = f"{acct} ({callback_url_acct_top_new_open})\n" \
                        f"New risks identified: {acct_data['top_new_open']}\n" \
                        f"New high risk alerts: {acct_data['top_new_high']}\n" \
                        f"Total risks identified: {acct_data['top_total']}\n\n"

                body += body2

        body3 = f"Top risks\n\n"

        body += body3
        #creates a sorted dictionary using sorted and lambda
        risks_sorted = {val[0]: val[1] for val in sorted(risks.items(), key=lambda x: (-x[1], x[0]))}
        #uses items and list slicing to product dictionary with first 5 key/value pairs
        top5risks = dict(list(risks_sorted.items())[0: 5])

        for policy, count in top5risks.items():

            body4 = f"{policy}:{count}\n"
            body += body4

        self.email_send.send_email('Daily Risk Summary', body, email_addr)

    def build_email_acct_list(self, toplevel_data, acctlevel_data, summarylevel_data, callback, email_list):
        new_accts = defaultdict(dict) # To store a revised list of accounts per email address
        for emailaddr, acctids in email_list.items():
            for acct in acctids:
                for acct_id,data in acctlevel_data.items():
                    if acct == acct_id:
                        new_accts[acct_id].update(data)
            self.build_email(toplevel_data, new_accts, summarylevel_data, callback, emailaddr)

    def run(self):
        callback = self.map_callback()
        print("Gathering top level data from tenant...")
        toplevel_data = self.gather_toplevel()
        print("Gathering account level data from tenant...")
        acctlevel_data = self.gather_acctlevel()
        print("Gathering summary level risk data from tenant...")
        summarylevel_data = self.gather_top_risks()
        print("Constructing email recipient list")
        email_list = self.build_email_list()
        print("Building and sending email...")
        self.build_email_acct_list(toplevel_data, acctlevel_data, summarylevel_data, callback, email_list)



def main():
    PCAlertEmailReport().run()


if __name__ == "__main__":
    main()