# Admiral

Script to manage CoreOS fleet

## Installation:

Tested with Python 3.4

```
git clone https://github.com/vespian/admiral.git
<setup virtualenv if desired>
cd admiral
pip install -r ./requirements.txt
./setup.py install
```

## Usage:
There can be only one copy of a pod running in given environment. It is by design,
due to the fact that mutliple copies of the same pod may generate conflicts such
as "Socket already in use" errors when forwarding port to the host. Environments
allow the operator to specify different ports/links/etc... on per-environment
basis.

The config file is templated using jinja2 syntax, detailed documentation can
be found at: http://jinja.pocoo.org/docs/dev/

Script allows for pod:
 * addition/removal (`add`/`remove`)
 * checking the state of the cluster (`list` subcommand)
 * changing the state of the pod to/from 'inactive', 'loaded', 'launched' ('set_state` subcommand)

Script has some PyDOC documentation and a built-in help:
```
admiral --help
admiral add --help
admiral list --help
...
```
In examples/ directory a sample configuration file can be found. It's syntax is
as follows:
 * fleet_ip, fleet_port: connection settings for fleet cluster
 * environements: a hash containing enviroments as subhashes, each one defining
                  custom variables for given environment
 * pods: a hash with subhashes describing pods. Each pod is made of individual
         services/containers with their name as a hash key. Attributes permitted
         are as follows:
         image: image to use for starting the container
         binds_to: check http://www.freedesktop.org/software/systemd/man/systemd.unit.html,
                   used for making units depending on each other so that they live
                   and die together
         machine_of: check https://coreos.com/fleet/docs/latest/unit-files-and-scheduling.html,
                   used for collocating containers together
         external_ports: ports to expose for given container, passed directly to
                         docker's "--publish" parameter
         links: links to create, passed directly to docker's "--link" parameter

##FIXME's/TODO's/problems:
- not sure if the same or better effect could be achieved with giant swarm's tool,
  or i.e. kubernetes.
- set_state method from fleet.py is passed to much data, interface should be
  timmed down
- there is no config data validation, python's cerberus should do the job. Please
  check config file's comments for details
- not sure how to make subcommands mandatory with click, currently it is possible
  to run "admiral" and get just empty output
- the python library I use to connect to fleet does not handle exceptions well:
  "TypeError: the JSON object must be str, not 'bytes'", some patching may be needed
- I was thinking about writting it in GO, but I think that Python would be much
  better suited for that and the performance of GO is not needed here anyway
- I have not tried to implement routing - this is quite big task already :)
- there are no unittests, before releasing it to the production they may be necessary
  (i.e. accidentally removing a cluster would be bad :))
- the collocation and service linking (one dies - all die) needs some love, I do
  not think that current solution (MachineOf + BindsTo) is bullet proof. Also, it
  would be nice to automate it somehow, but this is a complex topic.


All feedback appreciated !
