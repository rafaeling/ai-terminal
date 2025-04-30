# models/app.py

from assets import response

class App:
    """Manages app logic."""

    def __init__(self):
        self.response = response.response_text
    
    def print_response(self):
        print(self.response)

    def get_commands(self):
        command_list = []
        command = False
        for line in self.response.strip().split('\n'):
            if '```bash' in line:
                command = True
                continue
            elif '```' in line:
                command = False
                print("\n\n")
                continue
            
            if command == True and not line.startswith('#') and not line.strip() == "":
                print(line.lstrip())
                command_list.append(line.lstrip())
        return command_list
        
    def set_response(self, response):
        self.response = response
        
    def delete_cell(self):
        a =" "