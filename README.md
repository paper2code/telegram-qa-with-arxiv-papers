# Telegram QA with ArXiV papers - Paper2code

[![Open  In  Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/paper2code/telegram-qa-with-arxiv-papers/blob/master/notebooks/question-answering-with-arxiv-papers-at-scale.ipynb)

## Introduction
We will build a neural question and answering system using `transformers` models (`RoBERTa`). This approach is capable to perform Q&A across millions of documents in few seconds.
![alt text](docs/huggingace_telegram.png "Huggingface feat telegram")

## Quick start

### Clone the repository
```sh
git clone --depth=1 https://github.com/paper2code/telegram-qa-with-arxiv-papers
cd telegram-qa-with-arxiv-papers
mv .env-example .env
```

### Docker
For starting `telegram-qa-with-arxiv-papers` services with docker, please follow this [link](./docs/DOCKER.md).

## Data
For this tutorial, I will use ArXiV's research papers abstracts to do Q&A. The data is on Kaggle. [Go to dataset](https://www.kaggle.com/Cornell-University/arxiv). The dataset has many columns like 
- `id`
- `author`
- `title`
- `categories` 

but the columns we will be interested in are **`title`** and **`abstract`**.

`abstract` contains a long summary of the research paper. We will use this column to build our Question & Answer model.

Let's dive into the code.

## Let's Code
We will use Kaggle notebook to write our code so that we can leverage free GPU.

The format of the data is a nested `json`. We will limit our analysis to just 50,000 documents because of the compute limit on Kaggle to avoid `out of memory error`.

```python
import json
data  = []
with open("/opt/data/arxiv-metadata-oai.json", 'r') as f:
    for line in f: 
        data.append(json.loads(line))

# Limiting our analysis to 50K documents to avoid memory error
data = pd.DataFrame(data[:50000])

# Let's look at the data
data.head()
```
![alt text](docs/dataframe1.png "data frame")

We will use `abstract` column to train our QA model.

### Haystack
Now, Welcome `Haystack`! The secret sauce behind scaling up to thousands of documents is `Haystack`.
![alt text](docs/haystack1.png "Haystack")

`Haystack` helps you scale QA models to large collections of documents! You can read more about this amazing library here https://github.com/deepset-ai/haystack

For installation: `! pip install git+https://github.com/deepset-ai/haystack.git`

But just to give a background, there are 3 major components to Haystack.

- **Document Store**: Database storing the documents for our search. We recommend Elasticsearch, but have also more light-weight options for fast prototyping (SQL or In-Memory).
- **Retriever**: Fast, simple algorithm that identifies candidate passages from a large collection of documents. Algorithms include TF-IDF or BM25, custom Elasticsearch queries, and embedding-based approaches. The Retriever helps to narrow down the scope for Reader to smaller units of text where a given question could be answered.
- **Reader**: Powerful neural model that reads through texts in detail to find an answer. Use diverse models like BERT, RoBERTa or XLNet trained via FARM or Transformers on SQuAD like tasks. The Reader takes multiple passages of text as input and returns top-n answers with corresponding confidence scores. You can just load a pretrained model from Hugging Face's model hub or fine-tune it to your own domain data.

And then there is Finder which glues together a Reader and a Retriever as a pipeline to provide an easy-to-use question answering interface.

Now, we can setup `Haystack` in 3 steps:
 1. Install `haystack` and import its required modules
 2. Setup `DocumentStore`
 3. Setup `Retriever`, `Reader` and `Finder` 

### 1. Install `haystack`

Let's install `haystack` and import all the required modules
```python

# installing haystack
pip install git+https://github.com/deepset-ai/haystack.git

# importing necessary dependencies
from haystack import Finder
from haystack.indexing.cleaning import clean_wiki_text
from haystack.indexing.utils import convert_files_to_dicts, fetch_archive_from_http
from haystack.reader.farm import FARMReader
from haystack.reader.transformers import TransformersReader
from haystack.utils import print_answers
```
### 2. Setting up `DocumentStore`

Haystack finds answers to queries within the documents stored in a `DocumentStore`. The current implementations of `DocumentStore` include `ElasticsearchDocumentStore`, `SQLDocumentStore`, and `InMemoryDocumentStore`.

But they recommend `ElasticsearchDocumentStore` because as it comes preloaded with features like full-text queries, BM25 retrieval, and vector storage for text embeddings.

So - Let's set up a `ElasticsearchDocumentStore`.

```python
! wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.6.2-linux-x86_64.tar.gz -q
! tar -xzf elasticsearch-7.6.2-linux-x86_64.tar.gz
! chown -R daemon:daemon elasticsearch-7.6.2
 
import os
from subprocess import Popen, PIPE, STDOUT
es_server = Popen(['elasticsearch-7.6.2/bin/elasticsearch'],
                   stdout=PIPE, stderr=STDOUT,
                   preexec_fn=lambda: os.setuid(1)  # as daemon
                  )
# wait until ES has started
! sleep 30

# initiating ElasticSearch
from haystack.database.elasticsearch import ElasticsearchDocumentStore
document_store = ElasticsearchDocumentStore(host="localhost", username="", password="", index="document")
```

Once `ElasticsearchDocumentStore` is setup, we will write our documents/texts to the `DocumentStore`.


- Writing documents to `ElasticsearchDocumentStore` requires a format - List of dictionaries as shown below: 
```
[
    {"name": "<some-document-name>, "text": "<the-actual-text>"},
    {"name": "<some-document-name>, "text": "<the-actual-text>"}
    {"name": "<some-document-name>, "text": "<the-actual-text>"}
]
```

(Optionally: you can also add more key-value-pairs here, that will be indexed as fields in Elasticsearch and can be accessed later for filtering or shown in the responses of the Finder)

- We will use `title` column to pass as name and `abstract` column to pass as the text

```python
# Now, let's write the dicts containing documents to our DB.
document_store.write_documents(data[['title', 'abstract']].rename(columns={'title':'name','abstract':'text'}).to_dict(orient='records'))
```

### 3. Setup `Retriever`, `Reader` and `Finder`

Retrievers help narrowing down the scope for the Reader to smaller units of text where a given question could be answered. They use some simple but fast algorithm.

Here: We use Elasticsearch's default BM25 algorithm
```python
from haystack.retriever.sparse import ElasticsearchRetriever
retriever = ElasticsearchRetriever(document_store=document_store)
```
A Reader scans the texts returned by retrievers in detail and extracts the k best answers. They are based on powerful, but slower deep learning models.

Haystack currently supports Readers based on the frameworks FARM and Transformers. With both you can either load a local model or one from Hugging Face's model hub (https://huggingface.co/models).

Here: a medium sized RoBERTa QA model using a Reader based on FARM (https://huggingface.co/deepset/roberta-base-squad2)

```python
reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2", use_gpu=True, context_window_size=500)
```
And finally: The Finder sticks together reader and retriever in a pipeline to answer our actual questions.
```python
finder = Finder(reader, retriever)
```
## Voila! We're Done.
Once we have our `Finder` ready, we are all set to see our model fetching answers for us based on the question.

Below is the list of questions that I was asking the model
```python
prediction = finder.get_answers(question="What do we know about symbiotic stars", top_k_retriever=10, top_k_reader=2)
result = print_answers(prediction, details="minimal")
```
`Inferencing Samples: 100%|██████████| 1/1 [00:00<00:00,  1.17 Batches/s]`
`Inferencing Samples: 100%|██████████| 1/1 [00:00<00:00,  1.83 Batches/s]`
`Inferencing Samples: 100%|██████████| 1/1 [00:00<00:00,  1.71 Batches/s]`
`Inferencing Samples: 100%|██████████| 1/1 [00:00<00:00,  1.75 Batches/s]`
`Inferencing Samples: 100%|██████████| 1/1 [00:00<00:00,  1.78 Batches/s]`
`Inferencing Samples: 100%|██████████| 1/1 [00:00<00:00,  1.83 Batches/s]`
`Inferencing Samples: 100%|██████████| 1/1 [00:01<00:00,  1.08s/ Batches]`
`Inferencing Samples: 100%|██████████| 1/1 [00:01<00:00,  1.09s/ Batches]`
`Inferencing Samples: 100%|██████████| 1/1 [00:00<00:00,  1.83 Batches/s]`
`Inferencing Samples: 100%|██████████| 1/1 [00:00<00:00,  1.57 Batches/s]`
```
[   {   'answer': 'Their observed population in the\n'
                  'Galaxy is however poorly known, and is one to three orders '
                  'of magnitudes\n'
                  'smaller than the predicted population size',
        'context': '  The study of symbiotic stars is essential to understand '
                   'important aspects of\n'
                   'stellar evolution in interacting binaries. Their observed '
                   'population in the\n'
                   'Galaxy is however poorly known, and is one to three orders '
                   'of magnitudes\n'
                   'smaller than the predicted population size. IPHAS, the INT '
                   'Photometric Halpha\n'
                   'survey of the Northern Galactic plane, gives us the '
                   'opportunity to make a\n'
                   'systematic, complete search for symbiotic stars in a '
                   'magnitude-limited volume,\n'
                   'and discover a significant number of new '},
    {   'answer': 'Their observed population in the\n'
                  'Galaxy is however poorly known, and is one to three orders '
                  'of magnitudes\n'
                  'smaller than the predicted population size',
        'context': '  The study of symbiotic stars is essential to understand '
                   'important aspects of\n'
                   'stellar evolution in interacting binaries. Their observed '
                   'population in the\n'
                   'Galaxy is however poorly known, and is one to three orders '
                   'of magnitudes\n'
                   'smaller than the predicted population size. IPHAS, the INT '
                   'Photometric Halpha\n'
                   'survey of the Northern Galactic plane, gives us the '
                   'opportunity to make a\n'
                   'systematic, complete search for symbiotic stars in a '
                   'magnitude-limited volume,\n'
                   'and discover a significant number of new '}]

```

Let's try few more examples - 
```python
prediction = finder.get_answers(question="How is structure of event horizon linked with Morse theory?", top_k_retriever=10, top_k_reader=2)
result = print_answers(prediction, details="minimal")
```
`Inferencing Samples: 100%|██████████| 1/1 [00:00<00:00,  1.17 Batches/s]`
`Inferencing Samples: 100%|██████████| 1/1 [00:00<00:00,  1.83 Batches/s]`
`Inferencing Samples: 100%|██████████| 1/1 [00:00<00:00,  1.71 Batches/s]`
`Inferencing Samples: 100%|██████████| 1/1 [00:00<00:00,  1.75 Batches/s]`
`Inferencing Samples: 100%|██████████| 1/1 [00:00<00:00,  1.78 Batches/s]`
`Inferencing Samples: 100%|██████████| 1/1 [00:00<00:00,  1.83 Batches/s]`
`Inferencing Samples: 100%|██████████| 1/1 [00:01<00:00,  1.08s/ Batches]`
`Inferencing Samples: 100%|██████████| 1/1 [00:01<00:00,  1.09s/ Batches]`
`Inferencing Samples: 100%|██████████| 1/1 [00:00<00:00,  1.83 Batches/s]`
`Inferencing Samples: 100%|██████████| 1/1 [00:00<00:00,  1.57 Batches/s]`
```
[   {   'answer': 'in terms\nof the Morse theory',
        'context': '  The topological structure of the event horizon has been '
                   'investigated in terms\n'
                   'of the Morse theory. The elementary process of topological '
                   'evolution can be\n'
                   'understood as a handle attachment. It has been found that '
                   'there are certain\n'
                   'constraints on the nature of black hole topological '
                   'evolution: (i) There are n\n'
                   'kinds of handle attachments in (n+1)-dimensional black '
                   'hole space-times. (ii)\n'
                   'Handles are further classified as either of black or white '
                   'type, and only black\n'
                   'handles appear in real black ho'},
    {   'answer': 'in terms\nof the Morse theory',
        'context': '  The topological structure of the event horizon has been '
                   'investigated in terms\n'
                   'of the Morse theory. The elementary process of topological '
                   'evolution can be\n'
                   'understood as a handle attachment. It has been found that '
                   'there are certain\n'
                   'constraints on the nature of black hole topological '
                   'evolution: (i) There are n\n'
                   'kinds of handle attachments in (n+1)-dimensional black '
                   'hole space-times. (ii)\n'
                   'Handles are further classified as either of black or white '
                   'type, and only black\n'
                   'handles appear in real black ho'}]
```

One more - 
```python
prediction = finder.get_answers(question="What do we know about Bourin and Uchiyama?", top_k_retriever=10, top_k_reader=2)
result = print_answers(prediction, details="minimal")
```
`Inferencing Samples: 100%|██████████| 1/1 [00:00<00:00,  1.17 Batches/s]`
`Inferencing Samples: 100%|██████████| 1/1 [00:00<00:00,  1.83 Batches/s]`
`Inferencing Samples: 100%|██████████| 1/1 [00:00<00:00,  1.71 Batches/s]`
`Inferencing Samples: 100%|██████████| 1/1 [00:00<00:00,  1.75 Batches/s]`
`Inferencing Samples: 100%|██████████| 1/1 [00:00<00:00,  1.78 Batches/s]`
`Inferencing Samples: 100%|██████████| 1/1 [00:00<00:00,  1.83 Batches/s]`
`Inferencing Samples: 100%|██████████| 1/1 [00:01<00:00,  1.08s/ Batches]`
`Inferencing Samples: 100%|██████████| 1/1 [00:01<00:00,  1.09s/ Batches]`
`Inferencing Samples: 100%|██████████| 1/1 [00:00<00:00,  1.83 Batches/s]`
`Inferencing Samples: 100%|██████████| 1/1 [00:00<00:00,  1.57 Batches/s]`

```
[   {   'answer': 'generalised to non-negative concave\nfunctions',
        'context': ' ||| f(A+B) |||$ and $||| g(A)+g(B) ||| \\le\n'
                   '||| g(A+B) |||$, for any unitarily invariant norm, and for '
                   'any non-negative\n'
                   'operator monotone $f$ on $[0,\\infty)$ with inverse '
                   'function $g$. These\n'
                   'inequalities have very recently been generalised to '
                   'non-negative concave\n'
                   'functions $f$ and non-negative convex functions $g$, by '
                   'Bourin and Uchiyama,\n'
                   'and Kosem, respectively.\n'
                   '  In this paper we consider the related question whether '
                   'the inequalities $|||\n'
                   'f(A)-f(B) ||| \\le ||| f(|A-B|) |||$, and $||| g(A)-g(B)'},
    {   'answer': 'generalised to non-negative concave\nfunctions',
        'context': ' ||| f(A+B) |||$ and $||| g(A)+g(B) ||| \\le\n'
                   '||| g(A+B) |||$, for any unitarily invariant norm, and for '
                   'any non-negative\n'
                   'operator monotone $f$ on $[0,\\infty)$ with inverse '
                   'function $g$. These\n'
                   'inequalities have very recently been generalised to '
                   'non-negative concave\n'
                   'functions $f$ and non-negative convex functions $g$, by '
                   'Bourin and Uchiyama,\n'
                   'and Kosem, respectively.\n'
                   '  In this paper we consider the related question whether '
                   'the inequalities $|||\n'
                   'f(A)-f(B) ||| \\le ||| f(|A-B|) |||$, and $||| g(A)-g(B)'}]
```
The results are promising. Please note that we have used a pretrained model `deepset/roberta-base-squad2` for this tutorial. We might expect a significant improvement if we use a QA model trained specific to our dataset and then scale it up to millions of documents using `Haystack`

## Notebooks
- [Go to Dataset](https://www.kaggle.com/Cornell-University/arxiv)
- [Go to Published Kaggle Kernel](https://www.kaggle.com/officialshivanandroy/question-answering-with-arxiv-papers-at-scale)
- [Go to Google Colab Playground](https://colab.research.google.com/github/paper2code/telegram-qa-with-arxiv-papers/blob/master/notebooks/question-answering-with-arxiv-papers-at-scale.ipynb)

## Social Links
- [Go to Paper2Code's Website](https://paper2code.com)
- [Go to Paper2Code's Twitter](https://twitter.com/paper2code)
