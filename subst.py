#!/usr/bin/env python
"""Solve a crytogram puzzle"""
from __future__ import print_function

from collections import defaultdict, Counter
from string import ascii_uppercase
import re


def encode(word):
    """Helper function that gives canonical endocing to word"""
    canonical = {}
    for char in word:
        if char not in canonical:
            canonical[char] = len(canonical)
    return ''.join(chr(ord('a') + canonical[char]) for char in word)


def pattern_match(word, target_list):
    """Helper function to filter possible words against encoded word"""
    word_enc = encode(word)
    return [target for target in target_list if encode(target) == word_enc]


def all_upper(word):
    """Helper function to test if word is all uppercase / solved"""
    return len(word) == sum(c in set(ascii_uppercase) for c in word)


def subst(word, trial_solve):
    """Perform a substitution against a (partial) solution"""
    # assert not (set(trial_solve.keys()) - set(ascii_lowercase))
    # assert not (set(trial_solve.values()) - set(ascii_uppercase))
    # assert len(set(trial_solve.values())) == len(trial_solve)
    return ''.join(trial_solve.get(c, c) for c in word)


def _crypt_solve(target_words, possible_words, solution, dict_words, letter_freq):
    """Recursive solver"""
    # If all words have substituted uppercase letters we are done
    assert len(solution) == len(solution.values())
    solved_words = [word for word in target_words if all_upper(word)]
    if len(solved_words) == len(target_words):
        # print("yielding: {}".format(target_words))
        yield ' '.join(solved_words)
    else:
        # Is there a solved word that is not possible?
        for word in solved_words:
            if word.lower() not in dict_words:
                break
        else:
            # Is there an unsolved word that has no possible solutions?
            if not any(not poss and not all_upper(word) for word, poss in zip(target_words, possible_words)):
                possible_x = [set() for _ in target_words]
                for i, (word, poss) in enumerate(zip(target_words, possible_words)):
                    if word not in solved_words:
                        exc = (
                            '[^{}]'.format(
                                ''.join(c.lower() for c in sorted(solution.values()))
                            ) if solution else '.'
                        )
                        reg_word = ''.join(c.lower() if c.isupper() else exc for c in word)
                        regex = re.compile(reg_word)
                        possible_x[i] = set(dw for dw in poss if regex.match(dw))
                        if not possible_x[i]:
                            break
                    else:
                        possible_x[i] = set()
                else:
                    # This is the best word to solve for -- fewest unknowns, most effective substitutions
                    solve_word, candidate_words = min(
                        [(word, possible) for (word, possible) in zip(target_words, possible_x) if possible],
                        key=lambda x: (len(x[1]), -sum(letter_freq[c] for c in x[0])),
                    )
                    for cand in candidate_words:
                        add = {
                            c: w.upper()
                            for c, w in zip(solve_word, cand)
                            if c.islower()
                        }
                        # Was there an improvement? Is it legal?
                        if add and not set(solution.values()).intersection(add.values()):
                            trial_solve = dict(solution.items() + add.items())
                            if subst(solve_word, trial_solve).lower() == cand:
                                trial_words = [subst(word, trial_solve) for word in target_words]
                                print('-' * 30)
                                print(trial_words)
                                print(target_words)
                                trial_possible_words = [
                                    pattern_match(word, possible_list)
                                    for word, possible_list in zip(trial_words, possible_x)
                                ]
                                for cand_sol in _crypt_solve(
                                        trial_words, trial_possible_words, trial_solve, dict_words, letter_freq
                                ):
                                    yield cand_sol


def crypt_solve(target, solution=None):
    """Setup tables and call recursive solver"""
    solution = solution or {}
    target = target.lower()
    target_words = [subst(word, solution) for word in target.split(' ')]
    print(target_words)
    letter_freq = Counter(target)

    with open("Downloads/sowpods.txt") as handle:
        words = {line.rstrip() for line in handle}

    dict_words = defaultdict(set)
    for word in words:
        dict_words[len(word)].add(word)
    one_letter = {'i', 'a', 'o'}
    dict_words[1] = one_letter
    words.update(one_letter)

    possible_words = [
        pattern_match(word, dict_words[len(word)])
        for word in target_words
    ]

    for sol in _crypt_solve(target_words, possible_words, solution, words, letter_freq):
        yield sol


def main():
    """Main driver"""
    """
    src = 'congratulations'
    target = encode(src)
    sol = {}
    """
    target = 'abcd def bghd icdjbf bcd kl dc img bccd fc dc nigcf dc bon cp bcf'
    target = 'k qlgm kg xqmc k gqkcp k wnokcy faylcks emymglwumi wng xqmc k ymg qfzm k tkisfema gqmo dnig amynula tfcngi'
    #arget = 'I hate it when I think I buying organic vegetables but when I get home I discover they just regular donuts'
    #sol = {c: d.upper() for c, d in zip('qlgm', 'hate')}
    print(set(crypt_solve(target)))

if __name__ == '__main__':
    main()
