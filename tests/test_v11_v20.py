import unittest
import yaml

from nomiconvert import convert_v11_v20

class V11toV20TestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(V11toV20TestCase, self).__init__(*args, **kwargs)
        self.maxDiff = 40000

    def assertEqualYaml(self, first, second):
        self.assertEqual(yaml.load(first), yaml.load(second))

    def test_invalid_yaml(self):
        try:
            convert_v11_v20("  : what\n:")
            assert False
        except Exception:
            pass

    def test_minimal(self):
        input = """
        header:
          services: {}
        """

        result = """
        application:
            interfaces: {}
            bindings: []
            components:
              workflow:
                type: workflow.Instance
                interfaces:
                  {}
                configuration:
                  configuration.workflows:
                    {}

        """
        self.assertEqualYaml(convert_v11_v20(input), result)

    def test_workflows(self):
        input = """
        header:
          services: {}
        launch:
          steps: []
        destroy:
          steps: []
        do-this:
          steps: []
        do-that:
          parameters:
            x: {}
          steps: []
          return:
            y: {value: {}}
            z: {value: {}}
        do-that-with-extra:
          parameters:
            x: {enum: {hello: howareyou}, description: helloarg}
          steps: []
          return:
            y: {value: {}, description: helloreturn}
        do.that:
          steps: []
        .do.anything.else:
          steps: []
        """

        result = """
        application:
            interfaces:
              actions:
                '*': bind(workflow#actions.*)
            bindings: []
            components:
              workflow:
                type: workflow.Instance
                interfaces:
                  actions:
                    do-this: receive-command()
                    do-that: receive-command(object x => object y, object z)
                    do-that-with-extra:
                      type: receive-command(object x => object y)
                      arguments:
                        x:
                          suggestions: {hello: howareyou}
                          name: helloarg
                      results:
                        y:
                          name: helloreturn
                configuration:
                  configuration.workflows:
                    launch:
                      steps: []
                    destroy:
                      steps: []
                    do-this:
                      steps: []
                    do-that:
                      steps: []
                      return:
                        y: {value: {}}
                        z: {value: {}}
                    do-that-with-extra:
                      steps: []
                      return:
                        y: {value: {}, description: helloreturn}
                    do.that:
                      steps: []
                    .do.anything.else:
                      steps: []

        """
        self.assertEqualYaml(convert_v11_v20(input), result)

    def test_launch_parameters(self):
        input = """
        header:
          services: {}
        launch:
          parameters:
            a: {}
            b: {type: "string"}
            c: {type: "list"}
            d: {enum: {key: value}, description: "hello"}
          steps: []
        """

        result = """
        application:
            interfaces:
              input:
                '*': bind(workflow#input.*)
            bindings: []
            components:
              workflow:
                type: workflow.Instance
                interfaces:
                  input:
                    a: configuration(object)
                    b: configuration(string)
                    c: configuration(list<object>)
                    d:
                      type: configuration(object)
                      suggestions: {key: value}
                      name: hello
                configuration:
                  configuration.workflows:
                    launch:
                      steps: []

        """
        self.assertEqualYaml(convert_v11_v20(input), result)

    def test_launch_return(self):
        input = """
        header:
          services: {}
        launch:
          steps: []
          return:
            a: {value: {}}
            b: {value: {}, description: "test"}
        """

        result = """
        application:
            interfaces:
              result:
                '*': bind(workflow#result.*)
            bindings: []
            components:
              workflow:
                type: workflow.Instance
                interfaces:
                  result:
                    a: publish-signal(object)
                    b:
                      type: publish-signal(object)
                      name: test
                configuration:
                  configuration.workflows:
                    launch:
                      steps: []
                      return:
                        a: {value: {}}
                        b: {value: {}, description: "test"}

        """
        self.assertEqualYaml(convert_v11_v20(input), result)

    def test_services(self):
        input = """
        header:
          services:
            a:
              x: consume-signal(string)

            b:
              y: send-command( => )
        launch:
          steps: []
          return: {}
        """

        result = """
        application:
          interfaces: {}
          bindings:
            - [service_a#a, workflow#a]
            - [service_b#b, workflow#b]
          components:
            service_a:
              type: reference.Service
              interfaces:
                a:
                  x: publish-signal(string)
            service_b:
              type: reference.Service
              interfaces:
                b:
                  y: receive-command( => )
            workflow:
              type: workflow.Instance
              required: [a, b]
              interfaces:
                a:
                  x: consume-signal(string)
                b:
                  y: send-command( => )
              configuration:
                configuration.workflows:
                  launch:
                    steps: []
                    return: {}

        """
        self.assertEqualYaml(convert_v11_v20(input), result)


    def test_all(self):
        input = """
        header:
          services:
            a:
              x: consume-signal(string)
            b:
              y: send-command( => )
        launch:
          parameters:
            a: {}
            b: {type: "string"}
            c: {type: "list"}
            d: {enum: {key: value}, description: "hello"}
          steps: []
          return:
            a: {value: {}}
            b: {value: {}, description: "test"}
        destroy:
          steps: []
        do-this:
          steps: []
        do-that:
          parameters:
            x: {}
          steps: []
          return:
            y: {value: {}}
            z: {value: {}}
        do-that-with-extra:
          parameters:
            x: {enum: {hello: howareyou}, description: helloarg}
          steps: []
          return:
            y: {value: {}, description: helloreturn}
        do.that:
          steps: []
        .do.anything.else:
          steps: []
        """

        result = """
        application:
          interfaces:
            input:
              '*': bind(workflow#input.*)
            actions:
              '*': bind(workflow#actions.*)
            result:
              '*': bind(workflow#result.*)
          bindings:
            - [service_a#a, workflow#a]
            - [service_b#b, workflow#b]
          components:
            service_a:
              type: reference.Service
              interfaces:
                a:
                  x: publish-signal(string)
            service_b:
              type: reference.Service
              interfaces:
                b:
                  y: receive-command( => )
            workflow:
              type: workflow.Instance
              required: [a, b]
              interfaces:
                input:
                  a: configuration(object)
                  b: configuration(string)
                  c: configuration(list<object>)
                  d:
                    type: configuration(object)
                    suggestions: {key: value}
                    name: hello
                a:
                  x: consume-signal(string)
                b:
                  y: send-command( => )
                actions:
                  do-this: receive-command()
                  do-that: receive-command(object x => object y, object z)
                  do-that-with-extra:
                    type: receive-command(object x => object y)
                    arguments:
                      x:
                        suggestions: {hello: howareyou}
                        name: helloarg
                    results:
                      y:
                        name: helloreturn
                result:
                  a: publish-signal(object)
                  b:
                    type: publish-signal(object)
                    name: test
              configuration:
                configuration.workflows:
                  launch:
                    steps: []
                    return:
                      a: {value: {}}
                      b: {value: {}, description: "test"}
                  destroy:
                    steps: []
                  do-this:
                    steps: []
                  do-that:
                    steps: []
                    return:
                      y: {value: {}}
                      z: {value: {}}
                  do-that-with-extra:
                    steps: []
                    return:
                      y: {value: {}, description: helloreturn}
                  do.that:
                    steps: []
                  .do.anything.else:
                    steps: []

        """
        self.assertEqualYaml(convert_v11_v20(input), result)
