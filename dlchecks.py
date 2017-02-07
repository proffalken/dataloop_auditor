#!/usr/bin/env python

import json
import yaml
import requests

import prettytable

with open("config.yml", 'r') as config_file:
    config = yaml.load(config_file)

default_headers = {
                   'authorization': "Bearer %s" % config['auth']['api_key'],
                   'content-type': "application/json"
                   }

default_url = "https://api.dataloop.io/v1/orgs/%s/accounts" % (
                                      config['auth']['organisation']
                                      )

# Get the list of agents for each account
def get_account_agents(account_name=None):
    account_agents = {}
    if account_name is not None:
        acc_agent_request = requests.request('GET', "%s/%s/agents" % ( default_url,
            account_name), headers=default_headers)
        if acc_agent_request is not None:
            for agent in json.loads(acc_agent_request.text):
                account_agents[agent['name']] = {}
                agent_plugins = get_agent_plugins(
                        account_name,
                        agent['id']
                        )
                account_agents[agent['name']] = agent
                account_agents[agent['name']]['checks'] = []
                account_agents[agent['name']]['checks'] = agent_plugins

    return account_agents

# Get the list of plugins associated with each agent
def get_agent_plugins(account_name, agent_id=None):
    agent_plugins = []
    if agent_id is not None:
        agent_plugin_request = requests.request('GET', "%s/%s/agents/%s/plugins" % (
            default_url,
            account_name,
            agent_id), headers=default_headers)
        if agent_plugin_request is not None:
            for plugin in json.loads(agent_plugin_request.text):
                agent_plugins.append(plugin)

    return agent_plugins

def get_account_rules(account_name=None):
    account_rules = {}
    if account_name is not None:
        acc_rule_request = requests.request('GET', "%s/%s/rules" % ( default_url,
            account_name), headers=default_headers)
        if acc_rule_request is not None:
            for rule in json.loads(acc_rule_request.text):
                account_rules[rule['name']] = {}
                rule_details = get_rule_details(
                        account_name,
                        rule['id']
                        )
                account_rules[rule['name']]['details'] = {}
                account_rules[rule['name']]['details'] = rule_details

    return account_rules

# Get the list of plugins associated with each agent
def get_rule_details(account_name, rule_id=None):
    rule_details = {}
    if rule_id is not None:
        rule_detail_request = requests.request('GET', "%s/%s/rules/%s/" % (
            default_url,
            account_name,
            rule_id), headers=default_headers)
        if rule_detail_request is not None:
            rule_details[rule_id] = {}
            rule_details[rule_id] = json.loads(rule_detail_request.text)

    return rule_details

org_info = {}
print("# Dataloop Check Information for %s" % config['auth']['organisation'])
for account in config['accounts']:
    org_info[account['name']] = {}
    acc_details = requests.request('GET', "%s/%s" % ( default_url,
        account['name']), headers=default_headers)
    org_info[account['name']]['acc_details'] = json.loads(acc_details.text)
    org_info[account['name']]['agents'] = get_account_agents(account['name'])
    org_info[account['name']]['rules'] = get_account_rules(account['name'])
    print("## Details for Account %s" % account['name'])
    print("### Agents in **_%s_**" % account['name'])
    account_table = prettytable.PrettyTable()
    account_table.hrules = prettytable.ALL
    account_table.align = "l"
    account_table.field_names = ["Agent Name", "Plugins"]
    for agent in org_info[account['name']]['agents']:
        agent_checks = ""
        for check in org_info[account['name']]['agents'][agent]['checks']:
            agent_checks = agent_checks + "- %s\n" % check['name']
        account_table.add_row([agent,agent_checks])
    print("```")
    print(account_table)
    print("```")
    print("### Rules and Thresholds in **_%s_**" % account['name'])
    rules_table = prettytable.PrettyTable()
    rules_table.hrules = prettytable.ALL
    rules_table.align = "l"
    rules_table.field_names = ["Rule Name", "Criteria", "Action"]
    for rule in org_info[account['name']]['rules']:
        rules_criteria = ""
        for rule_det in org_info[account['name']]['rules'][rule]['details']:
            for criteria in org_info[account['name']]['rules'][rule]['details'][rule_det]['criteria']:
                if criteria['condition']['threshold'] is False:
                    rules_criteria = rules_criteria + "- %s status\n" % (
                            criteria['metric']
                            )
                else:
                    rules_criteria = rules_criteria + "- %s %s %s\n" % (
                            criteria['metric'],
                            criteria['condition']['operator'],
                            criteria['condition']['threshold']
                            )
                actions = org_info[account['name']]['rules'][rule]['details'][rule_det]['actions']
                action_list = ""
                for action in actions:
                    action_list = action_list + "- %s to " % action['type']
                    if action['type'] == "EMAIL":
                        for email in action['details']['emails']:
                            action_list = action_list + "%s " % email
                        action_list = action_list + "\n"


        rules_table.add_row([rule, rules_criteria, action_list])
    print("```")
    print(rules_table)
    print("```")
