[zato-connection-registry](https://github.com/emre/zato-connection-registry) is a command line application/library to load, backup, restore REST connection definitions in Zato servers.

If you maintain lots of REST API service definitions and experiment Zato at the same time (spinning up new Zato instances for development, load balancing Zato's internal load balancer, etc.) then it may be a pain to migrate these services.

Of course, it's possible to do that migration with the internal Zato database. However, it's not much practical.

This tool uses Zato's [internal services](https://zato.io/blog/posts/public-api.html) to fetch and pull service definitions, and uses [zato-client](https://zato.io/docs/progguide/clients/python.html) package.

Backup files are stored in the JSON format.

Note: Since ```zato-client``` package is a requirement for this tool, and python2 only, zato-connection-registry is also a python2 project.


# Installation

TBA

# Commands

TBA


# Using zato-connection-registry as a library

TBA

# Limitations

TBA

# Running tests

TBA


