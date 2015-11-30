Manifest converter for Tonomi platform
======================================

Manifest transformer/converter between syntaxes.
Supported conversions:

 - v1.1 to v2.0
 
Example Usage
============

    # download example v1.0 manifest 
    curl https://raw.githubusercontent.com/chemikadze/starter-java-web/master/manifest.yml > /tmp/manifest-1.0.yml

    # convert it
    nomi-convert --from-syntax v1.1 --to-syntax v2.0 /tmp/manifest-1.0.yml /tmp/manifest-2.0.yml

    # check it is still valid using contrib-python-qubell-client cli tool
    $ nomi validate-manifest /tmp/manifest-2.0.yml && echo OK 
    Component 'workflow': workflow 'launch': The following variable is not in the workflow scope: lb-tier~hosts
    Component 'workflow': workflow 'launch': The following variable is not in the workflow scope: lb-tier~hosts
    OK
 
v1.1 to v2.0 example
====================

This example covers all supported features of v1.1 to v2.0 conversion:
header services are converted to corresponding `reference.Service`, 
launch parameters are converted to `input` interface, launch result is converted
to `result` interface, and workflows are exposed to `actions` interface.

This is input manifest:

    header:
      services:
        a:
          x: consume-signal(string)

        b:
          y: receive-command( => )
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
 
And this is output manifest:

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
