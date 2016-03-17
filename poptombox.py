from email import message_from_string
from poplib import POP3
import mailbox, argparse, getpass

def get_parser():
    class PasswordPromptAction(argparse.Action):
        def __init__(self,
                     option_strings,
                     dest=None,
                     nargs='?',
                     default=None,
                     required=False,
                     type=None,
                     metavar=None,
                     help=None):
            super(PasswordPromptAction, self).__init__(
                  option_strings=option_strings,
                  dest=dest,
                  nargs=nargs,
                  default=default,
                  required=required,
                  metavar=metavar,
                  type=type,
                  help=help)

        def __call__(self, parser, args, values, option_string=None):
            if not values:
                password = getpass.getpass()
            else:
                password = values
            setattr(args, self.dest, password)

    parser = argparse.ArgumentParser(description="Download a POP mailbox and \
                                                  store it locally as an mbox")
    parser.add_argument('filename', nargs='?', default=False, help="The filename \
                        to write the mbox as. Defaults to the username")
    parser.add_argument('server', help="The POP server's FQDN or IP")
    parser.add_argument('username', help="The username associated with the POP \
                                          mailbox")
    parser.add_argument('--password', action=PasswordPromptAction, required=True,
                        help="The password associated with the POP mailbox. If \
                              left blank, the program will prompt for a password")

    return parser


def main(username, password, server, filename):
    M = POP3(server)
    M.user(username)
    M.pass_(password)
    numMessages = len(M.list()[1])

    mbox = mailbox.mbox(filename)

    for i in range(numMessages):
        message_string = ""
        for j in M.retr(i+1)[1]:
            message_string += j
        
        message = message_from_string(message_string)

        mbox.add(message.as_string())
        mbox.flush()

    mbox.flush()
    mbox.close()


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    args = vars(args)

    if args['filename'] is False:
        args['filename'] = args['username']

    main(args["username"], args["password"], args["server"], args["filename"])
