import re
import difflib
from pyonepassword import OP
from pyonepassword.api.exceptions import (
    OPSigninException,
    OPItemGetException,
    OPNotFoundException,
    OPConfigNotFoundException
)

# kubectl create secret generic my-secret --dry-run=client --from-file=myfile<(1password-tool test-template /home/romedius/src/1password-tool/templates/test.yaml) -o yaml | kubeseal --cert /tmp/sealed-secrets/pub-sealed-secrets.pem

class onepasswordtool:
    def __init__(self):
        self.op = self.__do_signin()
        self.__get_vaults()
        self.__get_items()
    def __do_signin(self):
        if OP.uses_biometric():
            try:
                op = OP()
            except OPNotSignedInException:
                print("Uh oh! Sign-in failed")
                exit(-1)
        else:
            my_password = getpass.getpass(prompt="1Password master password:\n")
            op = OP(password=my_password)
        return op
    def __get_vaults(self):
        self.vaults = [vault['name'] for vault in self.op.vault_list()]
    def __get_items(self):
        self.items = {}
        self.all_items = []
        for i in self.op.item_list():
            self.items[i['vault']['name']] = i['title']
            self.all_items.append(i['title'])
    def __match_vault(self, target):
        results = difflib.get_close_matches(target, self.vaults, 1)
        if len(results) == 0:
            self.__get_vaults()
            results = difflib.get_close_matches(target, self.vaults, 1)
            if len(results) == 0:
                raise IndexError("No such vault found")
        return results[0]
    def match_item(self, target, vault=None):
        if vault is None:
            results = difflib.get_close_matches(target, self.all_items, 1)
            if len(results) == 0:
                self.__get_items()
                results = difflib.get_close_matches(target, self.all_items, 1)
            if len(results) == 0:
                raise IndexError("No such item found")
        results = difflib.get_close_matches(target, self.items[vault], 1)
        if len(results) == 0:
            self.items[vault] = [item['title'] for item in self.op.item_list(vault=vault)]
            results = difflib.get_close_matches(target, self.items[vault], 1)
            if len(results) == 0:
                raise IndexError("No such item found")
        return results[0]
    def __replace_variable(self, match):
        return self.get_item(match.group(1))
    def get_item(self, target):    
        onepass_target = target.split("/")
        if len(onepass_target) == 3:
            vault = self.__match_vault(onepass_target[0])
            field = onepass_target[2]
            item_str = self.match_item(onepass_target[1], vault=vault)
            item = self.op.item_get(item_str, vault=vault)
        elif len(onepass_target) == 2:
            field = onepass_target[1]
            item_str = self.match_item(onepass_target[0])
            item = self.op.item_get(item_str)
        else:
            raise NameError("Invalid target, format incorrect") 
        for f in item['fields']:
            if f['label'] == field:
                return f['value']
        return None
    def render_secret(self, input_file):
        with open(input_file, "r") as f_in:
            # Find all variables starting with $$
            text = f_in.read()
            pattern = re.compile(r"{{([ a-zA-Z0-9_:./]+)}}")
            while True:
                match = pattern.search(text)
                if not match:
                    break
                text = text[:match.start()] + self.__replace_variable(match) + text[match.end():]
            return text
