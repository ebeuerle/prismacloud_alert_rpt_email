import lib
from collections import defaultdict


class PCAlertEmailReport():
    def __init__(self):
        self.config = lib.ConfigHelper()
        self.pc_sess = lib.PCSession(self.config.pc_user, self.config.pc_pass, self.config.pc_cust,
                                     self.config.pc_api_base)
        self.email_send = lib.EmailHelper()

    def map_callback(self):
        if self.config.pc_api_base == "api.prismacloud.io":
            callback_base = "app.prismacloud.io"
        elif self.config.pc_api_base == "api2.prismacloud.io":
            callback_base = "app2.prismacloud.io"
        elif self.config.pc_api_base == "api3.prismacloud.io":
            callback_base = "app3.prismacloud.io"

        return callback_base

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


    def build_email(self, toplevel, acctlevel, summarylevel, callback_base):
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

            body4 = f"{policy}:\t\t\t\t{count:>5}\n"
            body += body4

        self.email_send.send_email('Daily Risk Summary', body)


    def run(self):
        callback = self.map_callback()
        print("Gathering top level data from tenant...")
        toplevel_data = self.gather_toplevel()
        print("Gathering account level data from tenant...")
        acctlevel_data = self.gather_acctlevel()
        print("Gathering summary level risk data from tenant...")
        summarylevel_data = self.gather_top_risks()
        print("Building and sending email...")
        self.build_email(toplevel_data, acctlevel_data, summarylevel_data, callback)

def main():
    PCAlertEmailReport().run()


if __name__ == "__main__":
    main()