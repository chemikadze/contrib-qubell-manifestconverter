import yaml
from copy import deepcopy


COMPONENT_TYPES = {
    None: "object",
    "bool": "bool",
    "int": "int",
    "string": "string",
    "double": "double",
    "list": "list<object>",
    "map": "map<object>",
}


def workflow_type_to_component_type(type):
    return COMPONENT_TYPES[type]


def _config_from_param(name, data):
    return _meta_from_param(name, data, template="configuration(%s)")


def _meta_from_param(name, data, template):
    datatype = workflow_type_to_component_type(data.get("type"))
    component_type = template % datatype
    extras = {}
    if data.get("description"):
        extras["name"] = data.get("description")
    if data.get("enum"):
        extras["suggestions"] = data.get("enum")
    if extras:
        extras["type"] = component_type
        return extras
    else:
        return component_type


def _command_from_workflow(name, data):
    args = []
    results = []
    extras = {}
    for (param_name, param) in _param_map(data.get("parameters", {})).iteritems():
        datatype = workflow_type_to_component_type(data.get("type"))
        param_meta = _meta_from_param(param_name, param, "%s")
        if isinstance(param_meta, dict):
            del param_meta["type"]
            extras['arguments'] = extras.get('arguments', {})
            extras['arguments'][param_name] = param_meta
        args.append("%s %s" % (datatype, param_name))
    for (return_name, return_) in data.get("return", {}).iteritems():
        if "description" in return_:
            extras['results'] = extras.get('results', {})
            extras['results'][return_name] = {"name": return_["description"]}
        results.append("object %s" % return_name)
    if not args and not results:
        pin_type = "receive-command()"
    else:
        pin_type = "receive-command(%s => %s)" % (", ".join(args), ", ".join(results))
    if extras:
        extras["type"] = pin_type
        return extras
    else:
        return pin_type


def _invert_service_interface(interface):
    result = {}
    for (k, v) in interface.iteritems():
        inverted = v.replace("consume-signal", "publish-signal")\
            .replace("send-command", "receive-command")
        result[k] = inverted
    return result


def _param_map(params):
    if isinstance(params, dict):
        return params
    elif isinstance(params, list):
        return dict(map(lambda d: d.items()[0], params))
    else:
        raise Exception("Unsupported parameters declaration")


def convert_v11_v20(content):
    input_ast = yaml.load(content)
    workflows = deepcopy(input_ast)
    if "header" in workflows:
        del workflows["header"]
    result_ast = {
        "application": {
            "interfaces": {},
            "bindings": [],
            "components": {
                "workflow": {
                    "type": "workflow.Instance",
                    "interfaces": {},
                    "configuration": {
                        "configuration.workflows": workflows
                    }
                }
            }
        }
    }
    launch_workflow = workflows.get('launch', {})
    config_parameters = _param_map(launch_workflow.get('parameters', {}))
    config_declarations = dict(map(lambda (k, v): (k, _config_from_param(k, v)), config_parameters.iteritems()))
    if config_declarations:
        del launch_workflow['parameters']
        result_ast['application']['components']['workflow']['interfaces']['input'] = config_declarations
        result_ast['application']['interfaces']['input'] = {"*": "bind(workflow#input.*)"}

    return_values = launch_workflow.get('return', {})
    return_declarations = {}
    for (return_name, return_) in return_values.iteritems():
        return_declarations[return_name] = _meta_from_param(return_name, return_, "publish-signal(%s)")
    if return_declarations:
        result_ast['application']['components']['workflow']['interfaces']['result'] = return_declarations
        result_ast['application']['interfaces']['result'] = {"*": "bind(workflow#result.*)"}

    actions_interface = {}
    for (name, workflow) in workflows.iteritems():
        if name == "launch" or name == "destroy":
            continue
        if "." in name:
            continue
        # TODO check used as macro
        actions_interface[name] = _command_from_workflow(name, workflow)
        if "parameters" in workflow:
            del workflow['parameters']
    if actions_interface:
        result_ast['application']['components']['workflow']['interfaces']['actions'] = actions_interface
        result_ast['application']['interfaces']['actions'] = {"*": "bind(workflow#actions.*)"}

    service_interfaces = input_ast.get("header", {}).get("services", {})
    for (interface_name, interface) in service_interfaces.iteritems():
        component_ast = {
            "type": "reference.Service",
            "interfaces": {
                interface_name: _invert_service_interface(interface)
            }
        }
        component_name = "service_%s" % interface_name
        result_ast['application']['components'][component_name] = component_ast
        result_ast['application']['components']['workflow']['interfaces'][interface_name] = interface
        result_ast['application']['bindings'].append(
            ["%s#%s" % (component_name, interface_name), "workflow#%s" % interface_name])

    if service_interfaces:
        result_ast['application']['components']['workflow']['required'] = list(service_interfaces.keys())

    return yaml.dump(result_ast)
