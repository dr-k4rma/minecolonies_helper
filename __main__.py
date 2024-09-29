###############################################################################
# Project: minecolonies_helper - __main__.py
# Author: Alexander "Karma" Karpov
# Date: 08 Sep. 2024
# Provides: Main file.
#
###############################################################################

### Commands
# mch
#   lookup : Looks up what each parameter does
#       worker : Role name
#   roles  : Writes out all possible roles
#   rec    : Recommend a job based on skill points
#       [skills ...] : Arguments in style <skill_name>:<value>
#   rrec   : List-style version of the rec command, where you fill in one field at a time

## Dependencies
import csv

from argparse import ArgumentParser
from prettytable import PrettyTable
from typing import Tuple, List, Any

## Config Values
__INFO_FILE_PATH = rf"{__file__}/../info.csv"

## Misc Values
__NORMALIZED_DATA = {}
__ROLES = {}
__SKILLS_LIST = [
    "athletics",
    "dexterity",
    "strength",
    "agility",
    "stamina",
    "mana",
    "adaptability",
    "focus",
    "creativity",
    "knowledge",
    "intelligence"
]

## Private Functions
def __skill_datum(datum:str) -> Tuple[str,int]:
    args = datum.split(":")
    return (args[0].lower(), int(args[1]),)

def __sort_skills_list(datum) -> bool:
    return datum[1]

def __safe_dict_access(target_dict, key, default) -> Any:
    if key in target_dict: return target_dict[key]
    return default

## Commands
def __cmd_lookup(args) -> None:
    worker:str = args.worker

    details:List[str] = __NORMALIZED_DATA[worker]

    print()
    print(worker.capitalize())
    print(f"{details[0].capitalize()} : {details[1]}")
    print(f"{details[2].capitalize()} : {details[3]}")

def __cmd_roles(args) -> None:
    global __ROLES

    print((", ").join([role.title() for role in __ROLES]))

def __cmd_recommend(args) -> None:
    skills:List[Tuple[str,int]] = args.skills

    skill_value_dict = {skill: value for (skill, value) in skills}

    # Sort the lsit
    skills.sort(
        key = __sort_skills_list,
        reverse = True
    )

    print(">>> Given parameters")
    for datum in skills:
        print(f"\t{datum[0].capitalize()}: {datum[1]}")
    print()

    weights = {role: 0 for role in __ROLES}
    
    for skill_data in skills:
        skill_name = skill_data[0]
        skill_value = skill_data[1]
        for role, role_data in __NORMALIZED_DATA.items():
            if skill_name in role_data:
                weights[role] += skill_value

    sorted_weights = list(weights.items())
    sorted_weights.sort(
        key = __sort_skills_list,
        reverse = True
    )

    table = PrettyTable()
    table.field_names = ["Score", "Role", "P. Skill", "V1", "S. Skill", "V2"]
    table.align = "l"

    for (role, score) in sorted_weights:        
        primary_skill = __NORMALIZED_DATA[role][0].capitalize()
        primary_value = __safe_dict_access(skill_value_dict, primary_skill.lower(), 0)

        secondary_skill = __NORMALIZED_DATA[role][2].capitalize()
        secondary_value = __safe_dict_access(skill_value_dict, secondary_skill.lower(), 0)

        # Guard
        if score == 0: continue
        if primary_value == 0: continue
        if secondary_value == 0: continue

        table.add_row([score, role.capitalize(), primary_skill, primary_value, secondary_skill, secondary_value])

    print(table)

def __cmd_rapid_recommend(args) -> None:
    global __SKILLS_LIST

    skills_args = {key: None for key in __SKILLS_LIST}

    # Gather data
    print(">>> Given parameters")
    for skill in __SKILLS_LIST:
        skills_args[skill] = int(input(f"\t{skill.capitalize()}: "))

    # Reformat data
    skills_tuple_list = [(skill, value,) for skill, value in skills_args.items()]

    # Faux object
    class _temp:
        skills = skills_tuple_list

    # Call other command
    __cmd_recommend(_temp)

## Go
if __name__=="__main__":
    # CSV parsing
    with open(__INFO_FILE_PATH, "r") as ifile:
        reader = csv.reader(
            ifile,
            delimiter = ",",
            skipinitialspace = True
        )
        for row in reader:
            row[1] = row[1].lower()
            row[3] = row[3].lower()
            __NORMALIZED_DATA[row[0].lower()] = row[1:]
    __ROLES = list(__NORMALIZED_DATA.keys())

    # Parser setup
    parser = ArgumentParser(
        prog = "MineColonies Helper (MCH)",
    )

    subparsers = parser.add_subparsers(
        required = True,
        dest = "sub"
    )

    #region lookup_parser
    lookup_parser = subparsers.add_parser(
        "lookup",
        help = "Lookup necessary skills by role"
    )

    lookup_parser.add_argument(
        "worker",
        type = str.lower,
        help = "Role"
    )
    #endregion lookup_parser

    #region roles
    roles_parser = subparsers.add_parser(
        "roles",
        help = "List roles"
    )
    #endregion roles

    #region recommend
    recommend_parser:ArgumentParser = subparsers.add_parser(
        "rec",
        help = "Recommend a job based on skill points"
    )

    recommend_parser.add_argument(
        "skills",
        nargs = "+",
        help = "List of skills, must be in format 'skill:value'",
        type = __skill_datum
    )
    #endregion recommend

    #region rapid recommend
    rapid_recommend_parser:ArgumentParser = subparsers.add_parser(
        "rrec",
        help = "List-style version of the rec command, where you fill in one field at a time."
    )
    #endrefgion rapid recommend

    # Parsing
    args = parser.parse_args()
    
    {
        "lookup": __cmd_lookup,
        "roles": __cmd_roles,
        "rec": __cmd_recommend,
        "rrec": __cmd_rapid_recommend
    }[args.sub](args)