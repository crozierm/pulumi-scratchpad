# pulumi-scratchpad
## Prerequisites
- install uv: curl -LsSf https://astral.sh/uv/install.sh | sh
- install pulumi: brew install pulumi

## Instructions

- git clone git@github.com:crozierm/pulumi-scratchpad.git
- cd pulumi-scratchpad
- uv sync
- uv run pulumi stack select
- - enter a passphrase, or none
- - create a new stack or use an existing one
- uv run pulumi config set crozierm-pulumi-scratchpad:home_ip YOUR_HOME_IP
- uv run pulumi up

## Things I'd like, in no particular priority
* Unit test patterns (I don't care about coverage for my toy account)
* Account niceties (for my dev account)
* * CloudTrace
* * CloudWatch
* * Flow logs
* Are EKS cluster services reachable from bastion
* Get a kafka cluster running, probably with Strimzi
* * Or consider Pulsar?
* Default tagging (I forget the Pulumi nomenclature for this?)
* S3 buckets with mock data
* Polaris data catalog
* Trino in Kafka
* Spark in Kafka


