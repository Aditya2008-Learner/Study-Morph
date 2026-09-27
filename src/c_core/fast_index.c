#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <math.h>

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

EXPORT int c_levenshtein(const char *s1, const char *s2) {
    if (!s1 || !s2) return -1;
    int len1 = (int)strlen(s1);
    int len2 = (int)strlen(s2);
    if (len1 == 0) return len2;
    if (len2 == 0) return len1;

    int *prev_row = (int *)malloc((len2 + 1) * sizeof(int));
    int *curr_row = (int *)malloc((len2 + 1) * sizeof(int));
    if (!prev_row || !curr_row) {
        if (prev_row) free(prev_row);
        if (curr_row) free(curr_row);
        return -1;
    }

    for (int j = 0; j <= len2; j++) prev_row[j] = j;
    for (int i = 0; i < len1; i++) {
        curr_row[0] = i + 1;
        char c1 = (char)tolower((unsigned char)s1[i]);
        for (int j = 0; j < len2; j++) {
            char c2 = (char)tolower((unsigned char)s2[j]);
            int cost = (c1 == c2) ? 0 : 1;
            int insert_cost = curr_row[j] + 1;
            int delete_cost = prev_row[j + 1] + 1;
            int replace_cost = prev_row[j] + cost;
            int min_cost = insert_cost < delete_cost ? insert_cost : delete_cost;
            if (replace_cost < min_cost) min_cost = replace_cost;
            curr_row[j + 1] = min_cost;
        }
        for (int j = 0; j <= len2; j++) prev_row[j] = curr_row[j];
    }
    int result = prev_row[len2];
    free(prev_row); free(curr_row);
    return result;
}

EXPORT double c_fuzzy_similarity(const char *s1, const char *s2) {
    if (!s1 || !s2) return 0.0;
    int len1 = (int)strlen(s1);
    int len2 = (int)strlen(s2);
    if (len1 == 0 && len2 == 0) return 1.0;
    if (len1 == 0 || len2 == 0) return 0.0;
    int dist = c_levenshtein(s1, s2);
    if (dist < 0) return 0.0;
    int max_len = len1 > len2 ? len1 : len2;
    return 1.0 - ((double)dist / (double)max_len);
}

EXPORT double c_bm25_term_score(int tf, int doc_len, double avg_doc_len, int doc_count, int df, double k1, double b) {
    if (tf <= 0 || df <= 0 || doc_count <= 0 || avg_doc_len <= 0.0) return 0.0;
    double idf = log(1.0 + ((double)(doc_count - df) + 0.5) / ((double)df + 0.5));
    if (idf < 0.0) idf = 0.0;
    double len_norm = 1.0 - b + b * ((double)doc_len / avg_doc_len);
    double tf_norm = ((double)tf * (k1 + 1.0)) / ((double)tf + k1 * len_norm);
    return idf * tf_norm;
}

EXPORT void c_batch_bm25_scores(
    const int *tfs, const int *doc_lens, int num_docs,
    double avg_doc_len, int total_docs, int df,
    double k1, double b, double *out_scores
) {
    if (!tfs || !doc_lens || !out_scores || num_docs <= 0) return;
    double idf = log(1.0 + ((double)(total_docs - df) + 0.5) / ((double)df + 0.5));
    if (idf < 0.0) idf = 0.0;
    for (int i = 0; i < num_docs; i++) {
        int tf = tfs[i];
        if (tf <= 0) { out_scores[i] = 0.0; continue; }
        int doc_len = doc_lens[i];
        double len_norm = 1.0 - b + b * ((double)doc_len / avg_doc_len);
        double tf_norm = ((double)tf * (k1 + 1.0)) / ((double)tf + k1 * len_norm);
        out_scores[i] = idf * tf_norm;
    }
}

EXPORT unsigned long long c_fnv1a_hash(const char *str) {
    if (!str) return 0ULL;
    unsigned long long hash = 14695981039346656037ULL;
    while (*str) {
        hash ^= (unsigned char)tolower((unsigned char)*str);
        hash *= 1099511628211ULL;
        str++;
    }
    return hash;
}