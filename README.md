# The current state of the software supply chain in regard to attestation and what can be done to improve it.

Current software is usually made with hundreds, if not thousands of third-party libraries and components from the open source ecosystem. A real challenge that companies face every day when trying to make their products secure is making sure all of these components come from the actual developers of the software --they need to be able to attest the software they are using. This is done to prevent supply chain attacks such as the recent Mimecast or Solarwinds attacks. Companies need to make sure that that they are not highjacked by a rogue developer or by a malicious third-party such as an APT through open-source libraries. My project will focus on shedding light on the current state of software attestation in the software industry. This will be done by running queries on the most comonly used packages and libraries in popular languages and hopefully highlight the current gaps in the efforts the software industry has been taking to address issues in the with supply chain security.

Specifically, I aim to answer the following questions:

- What is the current state of the software supply chain in regards to software attestation? Are software engineers building software that can be attested? What about building it in ways that can be reproduced?
- In general, is anyone able to confirm that a piece of software belongs to a specific publisher or developer? What about a specific organization?
- Who do the members of the software supply chain have to trust in order to be part of and benefit from the open-source ecosystem?
- What are the underlying assumptions when using third-party code? Is there an assumption that software is benign?
- How do members of the open-source ecosystem interact with and how do they rely on each other?
- Who is trusting whom in the system?

Furthermore:

- What are the current challenges when attesting software? Why do those challenges exist?
- What tools are available to deal with these problems/challenges?
- How could these tools be improved? What challenges are yet to be addressed?

My plan is to write a short research paper that reveals the current state of the software supply chain.

Current ideas include:

- Querying github and gitlab for the most common dependencies and analyzing whether they contain sigstore signatures and whether they meet SLSA specifications.
- Query top x most downloaded packages from the following package managers for attestation data:
  - npm (javascript) (api for npm: https://api.npms.io/v2/package/ docs for api: https://api-docs.npms.io/)
  - Maven (java) (api for maven: https://search.maven.org/ docs for api: https://search.maven.org/apis)
  - pip (python) (docs: https://pip.pypa.io/en/stable/user_guide/#verifying-packages) (pip api: https://pypi.org/pypi/)
  - gem (ruby) (see https://docs.seattlerb.org/rubygems/ for API) (api: https://rubygems.org/api/v1/gems/)
  - go (goLang) (docs: https://golangdocs.com/packages-in-golang) (api: https://pkg.go.dev/)
  - cargo (rust) (docs: https://doc.rust-lang.org/stable/book/) (api: https://crates.io/api/v1/crates)
  - nuget (.NET) (docs: https://docs.microsoft.com/en-us/nuget/what-is-nuget) (api: https://docs.microsoft.com/en-us/nuget/api/search-query-service-resource)
- As well as the following container managers:
  - docker (api: https://docs.docker.com/registry/spec/api/)


# How to run

Simply run docker-compose while building the docker file:

```bash
docker-compose up -d --build --no-deps --force-recreate
```

This will:

1. Build the container found in the scripts folder
2. Run three containers:
    - Elasticsearch to hold the analyzed data
    - Kibana to visualize the data
    - The container that runs the scripts that clone and analyze the code

The container (called `analysis`) will do the following:

1. Clone the top n packages of various programming languages and package managers (you can check `scripts/main.py` to see which ones)
1. Run analysis on the cloned code, which includes:
  - Check whether their commits are signed (using Git and GPG)
  - Check whether their dependencies have vulnerabilities (using snyk)
  - Check whether the code has any obvious security issues (using snyk code and semgrep)