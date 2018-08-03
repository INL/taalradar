
## Get OpenTaal data
Download OpenTaal source files from: https://www.opentaal.org/bestanden/file/2-woordenlijst-v-2-10g-bronbestanden
Extract the file: OpenTaal-210G-basis-gekeurd.txt


## Setup PyBOSSA project
Create project:
```
pbs --server http://localhost:5000 --api-key KEY create_project
```

If `template.html` or `long-description.md` have been changed, update project:
```
pbs --server http://localhost:5000 --api-key KEY update_project
```

Add tasks from tasks file. Set redundancy to 1, meaning that task is finished if 1 user has contributed:
```
pbs --server http://localhost:5000 --api-key KEY add_tasks --tasks-file opentaal_tasks.csv --redundancy 1
```

To delete ALL TASKS from the project (BEWARE):
```
pbs --server http://localhost:5000 --api-key KEY delete_tasks
```
