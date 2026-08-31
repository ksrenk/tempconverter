1. Port 5000 conflict on macOS

Problem
When starting the TempConverter container with Podman using host port 5000,
Podman returned an error indicating that the address was already in use.

Diagnosis
I used the following command to determine which process was listening on port 5000:

    lsof -nP -iTCP:5000 -sTCP:LISTEN

The output showed that the macOS Control Center process was already using
TCP port 5000.

Solution
Instead of changing the port used inside the container, I changed only the
host-side port mapping:

    -p 5001:5000

The Flask application continued listening on port 5000 inside the container
while the Mac exposed it on port 5001.

Verification
The application successfully opened at:

    http://localhost:5001

and temperature conversions were successfully stored in MySQL.

Reflection
This problem demonstrated the difference between container ports and host
ports. A service can continue using its expected internal port even when a
different host port must be selected because of a conflict.

2. Python test module import problem

Problem
The unit and integration tests initially failed with ModuleNotFoundError
errors for project modules such as converter and app.

Diagnosis
The files existed in the mounted project directory, so the failure was not
caused by missing source files. The problem occurred when pytest was invoked
directly in the temporary Python container.

Solution
I changed the test command from:

    pytest

to:

    python -m pytest

This executes pytest through the same Python interpreter and produced the
correct module search path for the project.

Verification
All five unit tests and both integration tests passed successfully.

Reflection
The Python interpreter used to launch a tool can affect module resolution.
Using `python -m pytest` makes the test execution environment more explicit
and reproducible.

3. GitHub Actions could not find the Dockerfile

Problem
The CI pipeline successfully reached the container build stage but failed
because Docker could not find the Dockerfile.

Diagnosis
The Dockerfile existed locally, but the command:

    git ls-files Dockerfile

showed that it was not tracked by Git. Attempting to add it also showed that
the file was being ignored by .gitignore.

The CI runner only receives files committed to the Git repository, so the
locally existing Dockerfile was not available in GitHub Actions.

Solution
I removed the incorrect Dockerfile ignore rule from .gitignore, added the
Dockerfile to Git and pushed the change to GitHub.

Verification
A new GitHub Actions run successfully reached and completed the Docker image
build step.

Reflection
A file existing in the local working directory does not mean that it is
available to a CI system. Build-critical files must be tracked in source
control.

4. Docker Swarm database startup race

Problem
During the initial Docker Swarm deployment, several TempConverter tasks failed
before the service eventually reached the required 2/2 running replicas.

Diagnosis
Docker Swarm service logs showed errors including:

    Can't connect to MySQL server on 'db'
    Name or service not known

and later:

    Connection refused

The Flask application calls `db.create_all()` during startup, so it requires
MySQL to be reachable immediately.

Cause
The TempConverter replicas were started while the MySQL service was still
being created and initialized. Service creation and service readiness are not
the same thing.

Solution
The TempConverter Swarm service used a restart policy. Swarm automatically
recreated failed tasks until MySQL finished initialization and became
available.

Verification
The final service state showed:

    tempconverter_app    2/2
    tempconverter_db     1/1

Both application replicas subsequently served successful HTTP requests and
stored conversions in MySQL.

Reflection
Distributed applications must tolerate dependencies that are temporarily
unavailable. Restart policies, health checks and application-level retry
logic are important because an orchestrator starting a service does not mean
that the service is immediately ready.
