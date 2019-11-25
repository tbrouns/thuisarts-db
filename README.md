This repository contains a basic scraper for [Thuisarts](https://thuisarts.nl).

The script produces three files:
- `thuisarts.yaml` contains topics along with an ID and a link to the summary
  page
- `thuisarts-synonyms.yaml` contains a mapping of topics from `thuisarts.yaml`
  to their synonyms (to create a larger index)
- `thuisarts-summaries` is a folder with <ID>.txt files, containing the summary
  text for the topic matching that ID
