## Altmetric Parser
This script pulls the identifiers for Publications in outbreak.info and pings the altmetric API with acceptable identifiers (dois and pmids). It formats the returned result as schema-compliant AggregateReviews which can be added to the record for the corresponding publication using the `evaluations` property.

The metadata is all dumped into a single json file for merging into the database.
The file path for the metadata dump can be set by changing the path set for the variable: `result_data_file`

Note that the credentials.json file contains the API key for altmetrics api and is needed to bypass rate limits, but does not provide additional data access. 

An example of the results is included in the `results` directory.