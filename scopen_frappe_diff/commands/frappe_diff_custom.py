import frappe
import json
import git
from git import GitCommandError
import os
import click


def generate_diff(app, source_branch, source_commit, target_branch, target_commit):
    path = frappe.get_app_path(app)
    git_path = os.path.split(path)[0]
    files_path = os.path.join(path, "fixtures")
    target_repo = git.Repo(git_path)

    if source_branch or source_commit:
        source_repo = git.Repo(git_path)
        source_repo.git.checkout(source_branch)
        custom_field_data = json.loads(
            source_repo.git.show(
                "%s:%s" % (source_repo.commit(source_commit),
                           os.path.join(app, "fixtures") + '/custom_field.json')))
        property_data = json.loads(
            source_repo.git.show(
                "%s:%s" % (source_repo.commit(source_commit),
                           os.path.join(app, "fixtures") + '/property_setter.json')))
    else:
        with open(files_path + '/custom_field.json') as f:
            custom_field_data = json.load(f)

        with open(files_path + '/property_setter.json') as f:
            property_data = json.load(f)

    target_repo.git.checkout(target_branch)
    custom_field_repo_file = {}
    try:
        custom_field_repo_file = json.loads(
            target_repo.git.show(
                "%s:%s" % (target_repo.commit(target_commit), os.path.join(app, "fixtures") + '/custom_field.json')))
    except GitCommandError as ex:
        click.secho(ex)
        click.secho("Error when previous version of custom_field ", fg="yellow")

    property_repo_file = {}
    try:
        property_repo_file = json.loads(
            target_repo.git.show(
                "%s:%s" % (target_repo.commit(target_commit), os.path.join(app, "fixtures") + '/property_setter.json')))
    except GitCommandError as ex:
        click.secho(ex)
        click.secho("Error when previous version of property_setter ", fg="yellow")

    # Custom fields declarations
    # List of deleted and added custom field in the new file
    new_custom_field = list()
    old_custom_field = list()
    # Result of the changes in the new custom field file with name as key and dict of the changed properties as value
    custom_field_after = dict()
    custom_field_before = dict()

    # Property setters declarations
    # List of deleted and added property in the new file
    new_property = list()
    old_property = list()
    # Result of the changes in the new property setter file with name as key and dict of the changed properties as value
    property_after = dict()
    property_before = dict()

    #Custom filed
    for file_custom_field in custom_field_data:

        add_custom_field = True

        for repo_custom_field in custom_field_repo_file:

            if repo_custom_field["name"] == file_custom_field["name"]:

                add_custom_field = False

                custom_field_after[file_custom_field["name"]] = dict()
                custom_field_before[repo_custom_field["name"]] = dict()

                for file_fieldtype, file_value in file_custom_field.items():

                    add_fieldtype = True

                    for repo_custom_field_fieldtype, repo_value in repo_custom_field.items():

                        if repo_custom_field_fieldtype == file_fieldtype:

                            if file_value == repo_value or file_fieldtype == "modified":
                                add_fieldtype = False

                    if add_fieldtype:
                        custom_field_after[file_custom_field["name"]][file_fieldtype] = file_value

                if not custom_field_after[file_custom_field["name"]]:
                    del custom_field_after[file_custom_field["name"]]

                for repo_fieldtype, repo_value in repo_custom_field.items():

                    add_fieldtype = True

                    for file_custom_field_fieldtype, file_value in file_custom_field.items():

                        if file_custom_field_fieldtype == repo_fieldtype:

                            if repo_value == file_value or repo_fieldtype == "modified":
                                add_fieldtype = False

                    if add_fieldtype:
                        custom_field_before[repo_custom_field["name"]][repo_fieldtype] = repo_value

                if not custom_field_before[repo_custom_field["name"]]:
                    del custom_field_before[repo_custom_field["name"]]

        if add_custom_field:
            new_custom_field.append(file_custom_field)

    for repo_custom_field in custom_field_repo_file:

        add_custom_field = True

        for file_custom_field in custom_field_data:

            if repo_custom_field["name"] == file_custom_field["name"]:
                add_custom_field = False

        if add_custom_field:
            old_custom_field.append(repo_custom_field)

    #Property Setter
    for file_property in property_data:

        add_property_setter = True

        for repo_property in property_repo_file:

            if repo_property["name"] == file_property["name"]:

                add_property_setter = False

                property_after[file_property["name"]] = dict()
                property_before[repo_property["name"]] = dict()

                for file_fieldtype, file_value in file_property.items():

                    add_fieldtype = True

                    for repo_property_fieldtype, repo_value in repo_property.items():

                        if repo_property_fieldtype == file_fieldtype:

                            if file_value == repo_value or file_fieldtype == "modified":
                                add_fieldtype = False

                    if add_fieldtype:
                        property_after[file_property["name"]][file_fieldtype] = file_value

                if not property_after[file_property["name"]]:
                    del property_after[file_property["name"]]

                for repo_fieldtype, repo_value in repo_property.items():

                    add_fieldtype = True

                    for file_property_fieldtype, file_value in file_property.items():

                        if file_property_fieldtype == repo_fieldtype:

                            if repo_value == file_value or repo_fieldtype == "modified":
                                add_fieldtype = False

                    if add_fieldtype:
                        property_before[repo_property["name"]][repo_fieldtype] = repo_value

                if not property_before[repo_property["name"]]:
                    del property_before[repo_property["name"]]

        if add_property_setter:
            new_property.append(file_property)

    for repo_property in property_repo_file:

        add_property_setter = True

        for file_property in property_data:

            if repo_property["name"] == file_property["name"]:
                add_property_setter = False

        if add_property_setter:
            old_property.append(repo_property)

    diff_html = open(files_path + "/diff.html", "w")
    diff_html.write("<!DOCTYPE html>\n<html lang=\"fr\">\n")
    diff_html.write("<head>\n")
    diff_html.write("<title>Diff file</title>\n")
    diff_html.write("<style>\n\
    table{\n\
        border: 1px solid black;\n\
        width: 80%;\n\
        margin-left: auto;\n\
        margin-right: auto;\n\
    }\n\
    th, td {\n\
        border: 1px solid black;\n\
    }\n\
    .child_table{\n\
        border: none;\n\
        width: 100%;\n\
    }\n\
    .child_td{\n\
        border: none;\n\
        width: 50%;\
    \n}\n</style>\n")
    diff_html.write("</head>\n")
    diff_html.write("<body>\n")
    diff_html.write("<table>\n<caption>\ncustom_field\n</caption>\n")
    diff_html.write("<thead>\n<tr>\n")
    diff_html.write("<th>Doctype</th>\n")
    diff_html.write("<th>Fieldname</th>\n")
    diff_html.write("<th>Before/After</th>\n")
    diff_html.write("</tr>\n</thead>\n")
    diff_html.write("<tbody>\n")

    for new_custom_field in new_custom_field:
        name = new_custom_field['name'].split("-")
        diff_html.write("<tr>\n")
        diff_html.write("<td>" + name[0] + "</td>\n")
        diff_html.write("<td>" + name[1] + "</td>\n")
        diff_html.write("<td>\n<table class=\"child_table\">\n")

        for name, value in new_custom_field.items():
            if name in ['doctype', 'fieldname', 'fieldtype', 'options']:
                diff_html.write("<tr>\n<td class=\"child_td\"></td>\n<td class=\"child_td\">" + name + " : " + str(
                    value) + "</td>\n</tr>\n")

        diff_html.write("</table>\n</td>\n")

        diff_html.write("</tr>\n")

    for old_custom_field in old_custom_field:
        name = old_custom_field['name'].split("-")
        diff_html.write("<tr>\n")
        diff_html.write("<td>" + name[0] + "</td>\n")
        diff_html.write("<td>" + name[1] + "</td>\n")
        diff_html.write("<td>\n<table class=\"child_table\">\n")

        for name, value in old_custom_field.items():
            if name in ['doctype', 'fieldname', 'fieldtype', 'options']:
                diff_html.write("<tr>\n<td class=\"child_td\">" + name + " : " + str(
                    value) + "</td>\n<td class=\"child_td\"></td>\n</tr>\n")

        diff_html.write("</table>\n</td>\n")
        diff_html.write("</tr>\n")

    for prev_custom_field, prev_items in custom_field_before.items():

        prev_custom_field_name = prev_custom_field.split("-")
        diff_html.write("<tr>\n")
        diff_html.write("<td>" + prev_custom_field_name[0] + "</td>\n")
        diff_html.write("<td>" + prev_custom_field_name[1] + "</td>\n")
        diff_html.write("<td>\n<table class=\"child_table\">\n<tbody>\n")

        for name, value in prev_items.items():

            diff_html.write("<tr>\n")
            diff_html.write("<td class=\"child_td\">" + name + " : " + str(value) + "</td>\n")

            if prev_custom_field in custom_field_after.keys() and name in custom_field_after[prev_custom_field]:

                diff_html.write(
                    "<td class=\"child_td\">" + name + " : " + str(
                        custom_field_after[prev_custom_field][name]) + "</td>\n")
                del custom_field_after[prev_custom_field][name]

            else:

                diff_html.write("<td class=\"child_td\"></td>\n")

            diff_html.write("</tr>\n")

        if prev_custom_field in custom_field_after.keys() and custom_field_after[prev_custom_field]:

            for name, value in custom_field_after[prev_custom_field].items():
                diff_html.write("<tr>\n<td class=\"child_td\"></td>\n<td class=\"child_td\">" + name + " : " + str(
                    value) + "</td>\n</tr>\n")

        if prev_custom_field in custom_field_after.keys():
            del custom_field_after[prev_custom_field]

        diff_html.write("<tbody>\n</table>\n</td>\n")
        diff_html.write("</tr>\n")

    for new_custom_field, new_items in custom_field_after.items():

        name = new_custom_field.split("-")
        diff_html.write("<tr>\n")
        diff_html.write("<td>" + name[0] + "</td>\n")
        diff_html.write("<td>" + name[1] + "</td>\n")
        diff_html.write("<td>\n<table class=\"child_table\">\n")

        for name, value in new_items.items():
            diff_html.write("<tr>\n<td class=\"child_td\"></td>\n<td class=\"child_td\">" + name + " : " + str(
                value) + "</td>\n</tr>\n")

        diff_html.write("</table>\n</td>\n")
        diff_html.write("</tr>\n")

    diff_html.write("</tbody>\n</table>\n")
    diff_html.write("<table>\n<caption>\nproperty_setters\n</caption>\n")
    diff_html.write("<thead>\n<tr>\n")
    diff_html.write("<th>Doctype</th>\n")
    diff_html.write("<th>Fieldname</th>\n")
    diff_html.write("<th>Property</th>\n")
    diff_html.write("<th>Before/After</th>\n")
    diff_html.write("</tr>\n</thead>\n")
    diff_html.write("<tbody>\n")

    for new_property in new_property:
        name = new_property['name'].split("-")
        diff_html.write("<tr>\n")
        diff_html.write("<td>" + name[0] + "</td>\n")
        diff_html.write("<td>" + name[1] + "</td>\n")
        diff_html.write("<td>" + name[2] + "</td>\n")
        diff_html.write("<td>\n<table class=\"child_table\">\n")

        for name, value in new_property.items():
            if name in ['doctype', 'doctype_or_field', 'field_name', 'property', 'value']:
                diff_html.write("<tr>\n<td class=\"child_td\"></td>\n<td class=\"child_td\">" + name + " : " + str(
                    value) + "</td>\n</tr>\n")

        diff_html.write("</table>\n</td>\n")
        diff_html.write("</tr>\n")

    for old_property in old_property:
        name = old_property['name'].split("-")
        diff_html.write("<tr>\n")
        diff_html.write("<td>" + name[0] + "</td>\n")
        diff_html.write("<td>" + name[1] + "</td>\n")
        diff_html.write("<td>" + name[2] + "</td>\n")
        diff_html.write("<td>\n<table class=\"child_table\">\n")

        for name, value in old_property.items():
            if name in ['doctype', 'doctype_or_field', 'field_name', 'property', 'value']:
                diff_html.write("<tr>\n<td class=\"child_td\">" + name + " : " + str(
                    value) + "</td>\n<td class=\"child_td\"></td>\n</tr>\n")

        diff_html.write("</table>\n</td>\n")
        diff_html.write("</tr>\n")

    for prev_property, prev_items in property_before.items():

        prev_property_name = prev_property.split("-")
        diff_html.write("<tr>\n")
        diff_html.write("<td>" + prev_property_name[0] + "</td>\n")
        diff_html.write("<td>" + prev_property_name[1] + "</td>\n")
        diff_html.write("<td>" + prev_property_name[2] + "</td>\n")
        diff_html.write("<td>\n<table class=\"child_table\">\n<tbody>\n")

        for name, value in prev_items.items():

            diff_html.write("<tr>\n")
            diff_html.write("<td class=\"child_td\">" + name + " : " + str(value) + "</td>\n")

            if prev_property in property_after.keys() and name in property_after[prev_property]:

                diff_html.write(
                    "<td class=\"child_td\">" + name + " : " + str(property_after[prev_property][name]) + "</td>\n")
                del property_after[prev_property][name]

            else:

                diff_html.write("<td class=\"child_td\"></td>\n")

            diff_html.write("</tr>\n")

        if prev_property in property_after.keys() and property_after[prev_property]:

            for name, value in property_after[prev_property].items():
                diff_html.write("<tr>\n<td class=\"child_td\"></td>\n<td class=\"child_td\">" + name + " : " + str(
                    value) + "</td>\n</tr>\n")

        if prev_property in property_after.keys():
            del property_after[prev_property]

        diff_html.write("<tbody>\n</table>\n</td>\n")
        diff_html.write("</tr>\n")

    for new_property, new_items in property_after.items():

        name = new_property.split("-")
        diff_html.write("<tr>\n")
        diff_html.write("<td>" + name[0] + "</td>\n")

        if len(name) < 3:

            diff_html.write("<td></td>\n")
            diff_html.write("<td>" + name[1] + "</td>\n")

        else:

            diff_html.write("<td>" + name[1] + "</td>\n")
            diff_html.write("<td>" + name[2] + "</td>\n")

        diff_html.write("<td>\n<table class=\"child_table\">\n")

        for name, value in new_items.items():
            diff_html.write("<tr>\n<td class=\"child_td\"></td>\n<td class=\"child_td\">" + name + " : " + str(
                value) + "</td>\n</tr>\n")

        diff_html.write("</table>\n</td>\n")
        diff_html.write("</tr>\n")

    diff_html.write("</tbody>\n</table>\n")
    diff_html.write("</body>\n</html>")
