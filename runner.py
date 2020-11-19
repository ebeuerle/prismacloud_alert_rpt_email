import lib
import json

class PCAlertEmailReport():
    def __init__(self):
        self.config = lib.ConfigHelper()
        self.rl_sess = lib.PCSession(self.config.pc_user, self.config.pc_pass, self.config.pc_cust,
                                     self.config.pc_api_base)


def main():
    run_PCAlertEmailReport = PCAlertEmailReport()
    

if __name__ == "__main__":
    main()