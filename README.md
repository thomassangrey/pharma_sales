# pharma_sales
Scalable Solution with relational database pilot project 

Python Files:
(in /src)
        event_profiler.py
        events.py
C files:
(in src/modules/query, src/modules/sort, src/modules/uitilities)

Instructions:
i) type ./run.sh from the root directory of the installation folder
2) or type ./run_test.sh from the insight_testsuite root folder

run.sh script should build the C-API extensions developed by this author (T.S.)

__________

Results:

i)  A correct PASS was obtained fromt the tests suite
ii) This project was time consuming for its comparative simplicity, mainly because I completed a relational database project under development. I decided to complete this project with string relational
queries necessary for the pharma_sales insight coding challenge.

ii) events.py uses built-ins developed in C using Py-C-API extension tools. Its executable is built in place when you run ./run.sh

iv) The relational database is able to do O[n*log(n)] sorting, multi-sorting, single queries, batch-queries of many types. Queries are of O[log(n)]. Queries are of the set relational type (range comparisons, unions, intersections, complements, etc.) or of point relational type (single value comparisons)

    A summary of relational database queries is given below:

    # set comparators
    v = events.SORT.v        # set intersection
    u = events.SORT.u        # set union
    c = events.SORT.c        # intersect complement
    lte = events.SORT.lte    # less than or equal to
    gte = events.SORT.gte    # greater than or equal to
    lt = events.SORT.lt      # less than
    gt = events.SORT.gt      # greater than 
    
    # point comparators
    n = events.SORT.n        # point comparison: nearest to
    # <, >, <=, >=, ==       # for point comparisons

vi) Scalability: To scale events.py (pharma_sales), first split master file into discrete portions containing unique drug names whereby sets of records indexed by drug name are disjoint sets across the node cluster (e.g. node 1 gets the drugs beginning with A, B, or C, node2 gets the drugs beggingin with B-F, and so on). This can be accomplished with a precursor sort assuming at least all drug names can be read into memory. Load balancing will be dtermined by this sort as well.

Specifically, inside event_profiler, iterate this pseud_ocode

    1)  Package the drug records of m drug types and send to a node
    2)  execute the following:
            drug_subtotals, drug_scripts = drug_sales(a_stream)
            subtotals_list = list(drug_subtotals.values())
            drug_name_list = list(drug_subtotals.keys())
            unique_scripts = list(drug_scripts.values())
    3)  unpack the analyzed data
    4)  recombine and resort for presentation

if the scalability constraints are more severe and a precursor drug name sort cannot be effected, column contraction procedure could be effected, effectively reducing data redundancies at each cluster heirarchical stage and creating special new resized database instances at each heirarchical level of scaling. I didn't implement this, but it is certainly necessary for streaming applications.





