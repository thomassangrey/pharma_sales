import subprocess
import sys
sys.path.append('./src/modules')
import sort_map
import query
import infix


class SUBSET(object):
    """Take a slice of the DB from records."""

    def __init__(self, a_db, records):
        """Set up sub DB."""
        pass

    def extract(self):
        """Pull the data from the files."""
        pass

    def refine(self):
        """Interpolate."""
        pass


class FILE(dict):
    """Create a container for a file's information."""

    def __init__(self, filename, header_lines=1):
        """Provide filename, and number of lines in header (default 1)."""
        def linecount(self, filename):
            """Get linecount."""
            wc_str = ["wc", "-l", filename]
            if (0 == subprocess.check_call(wc_str)):
                wc = subprocess.check_output(["wc", "-l", filename])
                print('\n')
                numlines = int(wc.decode().split('input/')[0])
            else:   # this is slow for big files
                numlines = len(self.__fo.readlines())
                self.__fo.seek(0)
                print("wc -l failed. Counting lines using readline() instead.")
            return numlines
        super().__init__()
        self.__header_lines = header_lines
        self.__fo = open(filename)
        self.__lc = linecount(self, filename) - header_lines
        self.__name = (filename.split('/'))[-1]
        self.__header = self.__fo.readline()
        # self.__data = enumerate(self.__fo, 0)
        self.__type = filename.split('/')[-1].split('.')[-2].split('-')[-1]

    @property
    def header(self):
        """Set the file header as one string."""
        return self.__header

    @property
    def name(self):
        """Set the name of the file."""
        return self.__name

    @property
    def lc(self):
        """Set line count."""
        return self.__lc

    @property
    def data(self):
        """Set enumerated file data beginning after header (line 1, not 0)."""
        return self.__data

    @property
    def filetype(self):
        """Set file type."""
        return self.__type

    @property
    def fo(self):
        """Set opened file object."""
        return self.__fo

    def generate_db_of_file(self):
        """Use to create database derived from file."""
        columns = self.header.strip('\n').split(',')
        data_mat = [[0] * (self.lc) for k in range(len(columns))]
        alph_cols = []
        float_cols = []
        alph_names = []
        # for i, line in self.data:
        for i in range(self.lc):
            line = self.fo.readline()
            linelist = line.split(',')
            linelist[-1] = linelist[-1].strip('\n')

            if (i == 0):
                jdx = -1
                for j in linelist:
                    jdx += 1
                    if j.isalpha():
                        alph_cols.append(jdx)
                        alph_names.append(columns[jdx])
                    else:
                        float_cols.append(jdx)

                for jdx in (float_cols):
                    data_mat[jdx][i] = float(linelist[jdx])

                if (len(alph_names) > 0):
                    print("Hashing columns: \n\t\t{0}".format(alph_names))
                    alph_mat = [[""] * (self.lc) for k in
                                range(len(alph_names))]
                    kdx = -1
                    for jdx in alph_cols:
                        kdx += 1
                        alph_mat[kdx][i] = linelist[jdx]

            else:
                for jdx in (float_cols):
                    data_mat[jdx][i] = float(linelist[jdx])

                if (len(alph_names) > 0):
                    kdx = -1
                    for jdx in alph_cols:
                        kdx += 1
                        alph_mat[kdx][i] = linelist[jdx]

        if (len(alph_names) > 0):
            self.hash_table = HASHBROWNS(data_mat, alph_mat,
                                         alph_names, columns,
                                         alph_cols, float_cols)
        idx = -1
        for col in columns:
            idx += 1
            a_sort = SORT(data_mat[idx])
            print('file is: {0}, column is: {1}'.format(self.name, col))
            a_sort.sortbymedian()
            self.update({col: a_sort})
        return self

    def append_column(self, a_column_list, column_name):
        """Append a column to the file DB.

        Should be indexed by record and append_column(...) will
        append as a SORT object.
        """
        self.update({column_name: SORT(a_column_list).sortbymedian()})
        pass


class STREAM(dict):
    """Set up a dict of file object for one or more files."""

    def __init__(self, eventnum, inputpath=None):
        """Give eventnum (int), base_directory."""
        self.__filetype = ['']
        if inputpath is None:
            base_dir = 'input/'
        #     base_dir = '/'.join(os.getcwd().split('/')) + \
        #         '/input/'
        else:
            base_dir = inputpath + '/'

        filebase = '/'.join(base_dir .split('/')) + \
            'itcont' + '_' + str(eventnum) + '_'
        self.__filetype = ['pharma_sales']
        super().__init__()

        for ft in self.__filetype:
            filepath = filebase + ft + '.txt'
            self.update({ft: FILE(filepath)})
        self.event = eventnum

    def make_db(self):
        """Create DB."""
        filetypes = tuple(self)
        if len(filetypes) > 0:
            for ft in filetypes:
                a_file = self[ft]
                self.update({ft: a_file.generate_db_of_file()})
        return self

    def __str__(self):
        """Print some useful updates about file reads."""
        for ft in self.__filetype:
            print('Input Files for event {0}: '.format(self.event))
            print('File name: {0}'.format(self[ft].name))
            print('Header: {0}'.format(self[ft].header))
            print('Line count: {0}'.format(self[ft].lc))
        return 'done...'

    def close(self):
        """Close open files."""
        for ft in self.__filetype:
            self[ft].fo.close()


class SORT(object):
    """Creates a sort object."""

    def __init__(self, series):
        """Provide a list object."""
        self.series = series
        self.original = list(series)
        self.length = len(self.series)
        self.lookup = list(range(0, self.length))
        self.records = []

    def sortbymedian(self):
        """Method sortbymedian."""
        self.lookup = sort_map.sort(self.series)
        self.binseries = sort_map.build_bin(self.series)
        return self

    def complement(self, a_sort, intersect_recs):
        """Determine the set complement of records."""
        records_compl = []
        if (not isinstance(a_sort.records, type(None))) and \
            (not isinstance(intersect_recs, type(None))):
            
            sorted_recs = SORT(list(a_sort.records))
            sorted_recs.sortbymedian()
            len_sortrec = len(a_sort.records)
            len_intersect = len(intersect_recs)
            if (len_sortrec == 0) | (len_intersect == 0):
                a_sort.records = (sorted_recs.series)
                return self
            else:
                idx = 0
                jdx = 0
                while (jdx < len_intersect):
                    while ((idx < len_sortrec) and
                            ((sorted_recs.series[idx]) !=
                             intersect_recs[jdx])):
                        records_compl.append(int(sorted_recs.series[idx]))
                        idx += 1
                    jdx += 1
                a_sort.records = (sorted_recs.series)
                return self
        else:
            print("a_sort or intersect are None type in complement.")
            return self

    def comparator(self, arg, relational):
        """Compare query records with queried records."""
        val_list = []
        if isinstance(arg, type(SORT)):
            if isinstance(arg.records, type(None)):
                print("The (r.h.s.) sort object has NULL records..")
                return self
            else:
                if len(arg.records) == 0:
                    print("The (r.h.s.) sort object has ZERO records..")
                    return self
                else:
                    print("Multi-search in progress...")
                    for i in arg.records:
                        val_list.append(i)
        else:
            val_list = arg
            if isinstance(self, type(list)):
                print("Both of the relational args cannot be lists")
                return self
        if isinstance(self.records, type(None)):
            # print("The (l.h.s.) sort object has NULL records..")
            return self
        else:
            if len(self.records) == 0:
                self.records = query.find(relational, val_list, self.original,
                                          self.series, self.lookup,
                                          self.binseries)
            else:
                self.records = query.find(relational, val_list, self.original,
                                          self.series, self.lookup,
                                          self.binseries, self.records)
            return self

    def intersect(self, a_sort):
        """Find intersection of querie records with queried records."""
        intersect = []
        a_sort_mt = isinstance(self.records, type(None))
        self_mt = isinstance(a_sort.records, type(None))

        if not a_sort_mt:
            if len(self.records) == 0:
                a_sort_mt = 1
                if not a_sort_mt:
                    return a_sort.records
                else:
                    return None
        if not self_mt:
            if len(a_sort.records) == 0:
                self_mt = 1
                if not self_mt:
                    return self.records
                else:
                    return None

        if ((not a_sort_mt) and (not self_mt)):
            relational = 'E'
            sorted_a_sort_recs = SORT(list(a_sort.records))
            sorted_self_recs = SORT(list(self.records))
            sorted_self_recs.sortbymedian()
            sorted_a_sort_recs.sortbymedian()
            sorted_self_recs.records = query.find(relational,
                                                  sorted_a_sort_recs.series,
                                                  sorted_self_recs.original,
                                                  sorted_self_recs.series,
                                                  sorted_self_recs.lookup,
                                                  sorted_self_recs.binseries)

            if not isinstance(sorted_self_recs.records, type(None)):
                for i in sorted_self_recs.records:
                    intersect.append(sorted_self_recs.lookup[i])
        return intersect

    def compound_sort(self, secondary):
        """Method compound sort."""
        if not isinstance(secondary, type(self)):
            print("Error using compound sort. Requires a sort object")
        else:
            kdx_cnt = -1
            for kdx in self.binseries['positions']:
                kdx_cnt += 1
                prim_run_length = self.binseries['run_lengths'][kdx_cnt]
                subseries = []
                prim_sub_lookup = []
                for jdx in range(prim_run_length):
                    val = secondary.original[self.lookup[kdx + jdx]]
                    subseries.append(val)
                sec_sub_lookup = (SORT(subseries).sortbymedian()).lookup
                for jdx in range(prim_run_length):
                    prim_sub_lookup.append(self.lookup[kdx +
                                                       sec_sub_lookup[jdx]])
                for jdx in range(prim_run_length):
                    self.lookup[kdx + jdx] = prim_sub_lookup[jdx]

    @infix.or_infix
    def gte(self, val_list):
        """Querie greater than or equal to, (usage: |gte|)."""
        relational = 'GTE'
        return self.comparator(val_list, relational)

    @infix.or_infix
    def lte(self, val_list):
        """Querie greater than or equal to, (usage: |lte|)."""
        relational = 'LTE'
        return self.comparator(val_list, relational)

    @infix.or_infix
    def lt(self, val_list):
        """Querie less than, (usage: |lt|)."""
        relational = 'LT'
        return self.comparator(val_list, relational)

    @infix.or_infix
    def gt(self, val_list):
        """Querie greater than, (usage: |gt|)."""
        relational = 'GT'
        return self.comparator(val_list, relational)

    @infix.or_infix
    def u(self, a_sort):
        """Get unique union of two sorts, (usage: |u|)."""
        intersect_rec = self.intersect(a_sort)
        self.complement(a_sort, intersect_rec)
        self.records = self.records + a_sort.records
        a_sort.records = list(self.records)
        return self

    @infix.or_infix
    def pipL(self, a_sort):
        """Querie "pipe" between two sorts.(NOT YET IMPLEMENTED) 

        Really just pipes the sort results of sort_1 into sort_2.
        Not any different than set intersection.
            Usage: sort_1 |pipL| sort_2
        """
        if not (a_sort.records is None):
            if not (self.records is None):
                if len(self.records) == 0:
                    self.records = list(a_sort.records)
                else:
                    self.records = list(self.intersect(a_sort))
        return NotImplementedError

    @infix.or_infix
    def pipR(self, a_sort):
        """Querie "pipe" between two sorts.(NOT YET IMPLEMENTED)

        Really just pipes the sort results of sort_1 into sort_2.
        Not any different than set intersection.
            Usage: sort_1 |pipR| sort_2
        """
        if not (self.records is None):
            if not (a_sort.records is None):
                if len(a_sort.records) == 0:
                    a_sort.records = list(self.records)
                else:
                    a_sort.records = list(self.intersect(a_sort))
        return NotImplementedError
    
    @infix.or_infix
    def v(self, a_sort):
        """Querie intersection of two sorts, (usage: |v|)."""
        self.records = self.intersect(a_sort)
        if isinstance(self.records, type(None)):
            a_sort.records = None
        else:
            a_sort.records = list(self.records)
        return self

    @infix.or_infix
    def c(self, a_sort):
        """Get complement of the intesection of self and a_sort(usage: |c|)."""
        intersect_rec = self.v(a_sort)
        a_sort.records = self.complement(a_sort, intersect_rec)
        self.records = self.complement(intersect_rec)
        self.records = self.records + a_sort.records
        a_sort.records = list(self.records)
        return NotImplementedError

    def __gt__(self, val_list):
        """Get point querie greater than val_list (usage: >)."""
        relational = 'g'
        return self.comparator(val_list, relational)

    def __lt__(self, val_list):
        """Get point querie less than val_list (usage: <)."""
        relational = 'L'
        return self.comparator(val_list, relational)

    def __ge__(self, val_list):
        """Get point querie greater than or equal to val_list (usage: >=)."""
        relational = 'GE'
        return self.comparator(val_list, relational)

    def __le__(self, val_list):
        """Get point querie less than or equal to val_list (usage: <=)."""
        relational = 'LE'
        return self.comparator(val_list, relational)

    def __eq__(self, val_list):
        """Get point querie equal to val_list (usage: ==)."""
        relational = 'E'
        return self.comparator(val_list, relational)

    @infix.or_infix
    def n(self, val_list):
        """Get point querie nearest to val_list (usage: |n|)."""
        relational = 'N'
        return self.comparator(val_list, relational)
    
    def reset(self):
        self.records = []


class HASHBROWNS(dict):
    """Hash string matrix (alph_mat) and update numeric matrix in place.

    Numeric matrix updated with hashed column values at alph_cols
    locations. alph_cols are the header names of the string
    columns. all_cols are the header names of all columns.
    Also returns:

     dict(alph_col1_head: {hash11: string11, hash12: string12,..},
            alph_col2_head: {hash21: string21, hash22: string22,..}}
    """

    def __init__(self, mat, alph_mat=None, alph_names=None, all_names=None,
                 alph_cols=None, float_cols=None):
        """Hash a standalone string matrix or take optional arguments.

        Hash alpha_mat and insert at alpha_cols in num_mat
        (pre-initialized). Latter case requires list of alph_cols
        (headers) and full list of all_cols for final matrix.
        """
        if alph_mat is None:
            print("No hashes ... returning a numerical matrix")
            return None
        nc = len(alph_mat[0])
        nr = len(alph_mat)
        super().__init__()
        hashed = [[hash(alph_mat[jdx][idx])
                   for idx in range(nc)] for jdx in range(nr)]

        for jdx in range(nr):
            if (alph_names is None):
                colname = 'hash' + str(jdx)
            else:
                colname = alph_names[jdx]

            self.update({colname: dict({})})
            for idx in range(nc):
                self[colname].update({hashed[jdx][idx]: alph_mat[jdx][idx]})
        if (mat is None):
            print("Error: numerical matrix mat required")
            pass
        else:
            if ((alph_names is None) | (all_names is None)):
                pass
                print("Error in hashbrowns__init__(). Need\
                       alph_cols and/or numeric_cols.")
            else:
                for i in range(len(alph_cols)):
                    for j in range(len(all_names)):
                        if (alph_names[i] == all_names[j]):
                            mat[j][:] = hashed[i][:]
        return None


class VIZ(object):
    """Make this VIZ class for visualization tools."""

    def __init__(self):
        """Make."""
        pass
