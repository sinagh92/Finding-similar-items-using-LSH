import csv
import time


def myhash(x):
    """ hash function """
    a = 1
    b = 1
    p = 15373875993579943603  # a large prime number
    h = (a * x + b) % p
    return h


def compute_jacard(q1, q2):
    """ Compute Jacard similarity"""
    intersection = 0
    union = 1
    for a in q1:
        for b in q2:
            if a == b:
                intersection = intersection + 1
                break
    union = len(q1) + len(q2) - intersection
    return intersection/union


def read_input(file):
    """ Reading the questions and ids and making pairs from the input file"""
    question = []
    qids = []
    pairs = []
    with open('question_4k.tsv', encoding="utf8") as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        for row in reader:
            qids.append(row[0])
            question.append(row[1])
            pairs.append([row[0], row[1]])

    return question, qids, pairs


def compute_similar_qids(questions):
    """ Computing the similar question ids using Jacard similarity in the naive way"""     
    qids_similar = [""] * len(questions)
    for index1 in range(1, len(questions)):
        for index2 in range(index1+1, len(questions)):
            q1 = questions[index1].strip().lower()[:-1].split()
            q2 = questions[index2].strip().lower()[:-1].split()
            similarity = compute_jacard(q1, q2)
            if similarity > 0.6 and q1 != q2:
                if qids_similar[index1] == "":
                    qids_similar[index1] = qids[index2]
                else:
                    qids_similar[index1] = qids_similar[index1] + \
                        ","+qids[index2]
    return qids_similar


def write_results(file, qids, qids_similar):
    """ Writing the results in the output file""" 
    with open(file, "w") as record_file:
        record_file.write("qid"+"\t"+"similar-qids\n")
        for i in range(1, len(qids)):
            record_file.write(str(qids[i]) + "\t" + qids_similar[i] + "\n")


if __name__ == '__main__':

    time_start = time.clock()

    # read input file
    questions, qids, pairs = read_input('question_4k.tsv')

    # question 1 algorithm
    qids_similar = compute_similar_qids(questions)

    # write output file
    write_results("question_sim_4k.tsv", qids, qids_similar)

    # Compute timing
    time_elapsed = (time.clock() - time_start)
    print(time_elapsed)
