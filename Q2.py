import csv
import time
import uuid
from fnv import *


def random_gen():
    rand64 = uuid.uuid4().int & (1 << 64) - 1
    return rand64


def hash_function(x, r, s, r_weights):
    """ Computing the hash function"""
    a = r_weights[s][r][0]
    b = r_weights[s][r][1]
    p = 15373875993579943603
    h = (a * x + b) % p
    return h


def hash_for_table(x):
    """ Computing the hash function for the hash tables"""
    table_hash_a = random_gen()
    table_hash_b = random_gen()
    a = table_hash_a
    b = table_hash_b
    p = HashTable_size
    h = (a * x + b) % p
    return h


def compute_jacard(q1, q2):
    """ Compute Jacard similarity"""
    if len(q1) == 0 or len(q2) == 0:
        return 0
    else:
        intersection = 0
        union = 1
        for a in q1:
            for b in q2:
                if a == b:
                    intersection = intersection + 1
                    break
        union = len(q1) + len(q2) - intersection
        return intersection/union


def read_file(file):
    """ Reading the questions and ids and making pairs from the input file"""
    questions = []
    qids = []
    with open('question_150k.tsv', encoding="utf8") as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        for row in reader:
            qids.append(row[0])
            questions.append(row[1])

    questions_pair = dict(zip(qids, questions))
    qids_similar = dict(zip(qids, [[] for i in range(len(qids))]))

    return questions, qids_similar, qids, questions_pair


def initialize_hash_tables():
    """ Creating list parameters for hash tables"""
    r_weights = [[[[] for i in range(2)] for i in range(r)] for i in range(s)]
    for i in range(0, s):
        for j in range(0, r):
            r_weights[i][j][0] = random_gen()
            r_weights[i][j][1] = random_gen()

    H = [[[] for i in range(HashTable_size)] for i in range(s)]
    return H, r_weights


def fill_hash_tables(H, questions):
    """ Filling the hash tables with using min hash signature of the words in each question"""
    for i in range(1, len(questions)):
        question = questions[i].strip().lower()[:-1].split()
        min_hash_sig = []
        hashed_q = []
        for word in question:
            data = word.encode('utf-8')
            hashcode = hash(data, bits=64)  # fnv.fnv_1a is a default algorithm
            hashed_q.append(hashcode)
        for HashTable_index in range(0, s):
            min_hash_sig = 0
            for r_index in range(0, r):
                min_hash = 0xFFFFFFFFFFFFFFFF
                for hashed_w in hashed_q:
                    hashcode = hash_function(hashed_w, r_index,
                                      HashTable_index, r_weights)
                    if hashcode < min_hash:
                        min_hash = hashcode
                min_hash_sig = int(str(min_hash_sig) + str(min_hash))
            J = hash_for_table(min_hash_sig)
            H[HashTable_index][J].append(qids[i])
    return H


def find_similar_questions(H, questions_pair, qids_similar):
    """ Finding the similar questions based on the hash tables and do a final check with Jacard similarity"""  
    for HashTable_index in range(0, s):
        for row in range(0, HashTable_size):
            query = H[HashTable_index][row]
            for qid in query:
                for qid2 in query:
                    if qid != qid2:
                        q1 = questions_pair[qid].strip().lower()[:-1].split()
                        q2 = questions_pair[qid2].strip().lower()[:-1].split()
                        similarity = compute_jacard(q1, q2)
                        if similarity > 0.6 and q1 != q2:
                            repeated = 0
                            for qid_val in qids_similar[qid]:
                                if qid_val == qid2:
                                    repeated = 1
                            if repeated == 0:
                                temp_value = qids_similar[qid]
                                temp_value.append(qid2)
                                qids_similar[qid] = temp_value
    return qids_similar


def write_in_file(file, qids, qids_similar):
    """ Writing the results in the output file"""     
    with open("question_sim_150k.tsv", "w") as record_file:
        record_file.write("qid"+"\t"+"similar-qids\n")
        for i in range(1, len(qids)):
            result = " ".join(str(index)
                              for index in qids_similar[str(qids[i])]).replace(" ", ",")
            record_file.write(str(qids[i]) + "\t" + result + "\n")


if __name__ == '__main__':

    time_start = time.clock()

    r = 6
    s = 14
    HashTable_size = 104729

    H, r_weights = initialize_hash_tables()

    questions, qids_similar, qids, questions_pair = read_file(
        'question_150k.tsv')

    H = fill_hash_tables(H, questions)

    qids_similar = find_similar_questions(H, questions_pair, qids_similar)

    write_in_file("question_sim_150k.tsv", qids, qids_similar)

    time_elapsed = (time.clock() - time_start)
    print(time_elapsed)
