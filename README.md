## Scopen Frappe Diff

INSTALL 


       bench get-app bench get-app https://github.com/scopen-coop/scopen-frappe-diff.git

USAGE

       bench frappe-diff-custom [app-name] [OPTIONS]

OPTIONS

       --source-branch [arg]
              Source branch name, default : current branch
              
       --source-commit [arg]
              Source commit name, default : local files
              
       --target-branch [arg]
              Target branch name, default : current branch
              
       --target-commit [arg]
              Target commit name, default HEAD~1


DESCRIPTION

       This commands helps you compare two versions of custom_field.json and property_setter.json. 
       When launched, diff.html is generated in the fixtures folder of the app used on.
       With no options, it compares the last version commited and the local files.      

#### License

gpl-3.0
