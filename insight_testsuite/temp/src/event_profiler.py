import events
import cProfile
import pstats
import io

def drug_sales(a_stream):
    """Query a_stream for list of drug sales referenced by drug name.
    Use events database tool (Sangrey, 07/2018) with builtin modules sort and 
    query for fast database searches. 

    drug_sales uses hashed names for relational database purposes. Hashing strings
    is useful anyway for HIPPA regs and rules :) One query for drug name (hashed)
    is used to extract all relevant records for that drug. Further processing 
    is required in drug_prescriptions() to fill out the code challenge requirements
    for unique prescribers. Sales subtotals are also calculated here.original

    All results are stored in two dict()'s' for final sorting.
    """
    
    drug_subtotals = dict({})
    drug_scripts = dict({})

    sales = a_stream['pharma_sales']['drug_cost'].original
    drug_hash_table = a_stream['pharma_sales'].hash_table['drug_name']
    drug_hash_list = list(drug_hash_table.keys())
    drug_name_list = list(drug_hash_table.values())
    
    # Do query on drug names. Match to sales records
    for k, drug in enumerate(drug_hash_list):
        a_drug_query = (a_stream['pharma_sales']['drug_name'] == [drug])
        subtotal = 0
        for record in a_drug_query.records:
            subtotal += sales[record]

        drug_subtotals.update({drug_name_list[k]: int(subtotal)})
        prescriber_records = drug_prescriptions(a_stream, a_drug_query)
        drug_scripts.update({drug_name_list[k]: len(prescriber_records)})
        # reset query
        a_drug_query.reset()

    print(drug_subtotals)
    print(drug_scripts)

    return drug_subtotals, drug_scripts

def drug_prescriptions(a_stream, a_query=None):
    """Get unique prescribers.

    Use a "left-piped" query that pipes the record results of previous 
    drug-name query (see caller function drug_sales()). This query is then 
    subjected to two subsequent name match queries
    """
    
    prescriber_records = []

    prescribers_query_firstname = \
        a_stream['pharma_sales']['prescriber_first_name']
    prescribers_query_lastname = \
        a_stream['pharma_sales']['prescriber_last_name']
    
    # set comparators
    v = events.SORT.v        # set intersection
    

    firstname_hash_list = \
        [prescribers_query_firstname.original[k] for k in a_query.records]
    lastname_hash_list = \
        [prescribers_query_lastname.original[k] for k in a_query.records]

    

    for i, first_hash in enumerate(firstname_hash_list):
        if a_query is None:
            prescribers_query_firstname.records = []
            prescribers_query_lastname.records = []
        else:
            prescribers_query_firstname |v| a_query
            prescribers_query_lastname |v| a_query

        last_hash = lastname_hash_list[i]
        # compound query
        prescribers_query_lastname = \
        (prescribers_query_lastname == [last_hash])
        prescribers_query_firstname = \
            (prescribers_query_firstname == [first_hash])
        prescribers_query_firstname = prescribers_query_firstname |v| \
            (prescribers_query_lastname == [last_hash])
        if not isinstance(prescribers_query_firstname.records, type(None)):
            prescriber_records.append(len(prescribers_query_firstname.records))
        prescribers_query_firstname.reset()
        prescribers_query_lastname.reset()

    return prescriber_records
    
def string_number_compound_sort(string_list, number_list):
    """Return a list of sort order keys of type list[int].prescriber_records
    
    When given a unique list of strings, and numeric list, function returns
    the sort order  with primary order dictated by number_list and secondary
    sort order dictated by string_list
    """

    string_orderedMap = \
        sorted(enumerate(string_list), key= lambda x: x[1],reverse=False)
    string_ordinal = [0]*len(string_list)
    for i in range(len(string_orderedMap)):
        string_ordinal[string_orderedMap[i][0]] = i
    string_map_dict = dict()
    for k in range(len(string_list)):
        string_map_dict[str(string_ordinal[k])] = k

    str_o = string_ordinal

    ss_num = list(number_list)
    sm_num = events.SORT(ss_num)
    sm_num.sortbymedian()

    ss_str_o = list(str_o)
    sm_str_o = events.SORT(ss_str_o)
    sm_str_o.sortbymedian()
    events.SORT.compound_sort(sm_num, sm_str_o)
    strings = []
    for i in range(len(string_list)):
        strings.append(string_list[string_map_dict[str(sm_str_o.original[sm_num.lookup[i]])]])

    for i in range(len(string_list)):
        print("number_list[{0:2}] {1:8}= ,string_ordinal[{0:2}] = {2:8}".format(i, sm_num.series[i], strings[i]))
    
    sort_order = []
    for i in range(len(string_list)):
        sort_order.append(string_map_dict[str(sm_str_o.original[sm_num.lookup[i]])])
    return sort_order

def main():
    a_stream = events.STREAM(1)
    a_stream.make_db()
    print(a_stream['pharma_sales'])
    
    pr = cProfile.Profile()
    pr.enable()
    # Profile START

# SCALING:
# BEGIN DISTRIBUTED JOBS HERE

    drug_subtotals, drug_scripts = drug_sales(a_stream)
    subtotals_list = list(drug_subtotals.values())
    drug_name_list = list(drug_subtotals.keys())
    unique_scripts = list(drug_scripts.values())

# END DISTRUBUTED JOBS HERE
# CONCATENATE 3 RETURNED LISTS FROM EACH NODE
 
    new_fo = open("./output/top_cost_drug.txt",'w')
    sort_order = string_number_compound_sort(drug_name_list, subtotals_list)
    
    new_fo.write("drug_name,num_prescriber,total_cost\n")
    for i in reversed(sort_order):
        file_line = drug_name_list[i] + ',' + str(unique_scripts[i]) + \
            ',' + str(subtotals_list[i]) + '\n'
        new_fo.write(file_line)
        
        # Also print to screen:
        print("drug_name: {0},\t,drug_total: {1},\t,drug_sripts: {2}".\
            format(drug_name_list[i], subtotals_list[i], unique_scripts[i]))

    new_fo.close()
    a_stream.close()

if __name__ == "__main__":
    main()
print('\n...goodbye...')
