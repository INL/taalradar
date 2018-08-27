#!/bin/bash
server=""
key=""
redundancy=2

projects="analyse herken1 herken2"
for project in $projects
do
    echo "Creating $project"
    cd $project
    pbs --server $server --api-key $key create_project
    pbs --server $server --api-key $key update_project
    pbs --server $server --api-key $key delete_tasks
    tasks="$(find *.csv)"
    pbs --server $server --api-key $key add_tasks --tasks-file $tasks --redundancy $redundancy
    cd ..
done