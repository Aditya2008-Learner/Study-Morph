#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

EXPORT void c_rgb_to_grayscale(const unsigned char *rgb, unsigned char *gray, int width, int height) {
    if (!rgb || !gray || width <= 0 || height <= 0) return;
    int total = width * height;
    for (int i = 0; i < total; i++) {
        int r = rgb[i * 3];
        int g = rgb[i * 3 + 1];
        int b = rgb[i * 3 + 2];
        gray[i] = (unsigned char)((r * 299 + g * 587 + b * 114) / 1000);
    }
}

EXPORT int c_otsu_threshold(const unsigned char *gray, int width, int height) {
    if (!gray || width <= 0 || height <= 0) return 128;
    int total = width * height;
    int hist[256] = {0};
    for (int i = 0; i < total; i++) hist[gray[i]]++;
    double sum = 0.0;
    for (int i = 0; i < 256; i++) sum += (double)(i * hist[i]);
    double sumB = 0.0;
    int wB = 0, wF = 0;
    double varMax = 0.0;
    int threshold = 128;
    for (int t = 0; t < 256; t++) {
        wB += hist[t];
        if (wB == 0) continue;
        wF = total - wB;
        if (wF == 0) break;
        sumB += (double)(t * hist[t]);
        double mB = sumB / (double)wB;
        double mF = (sum - sumB) / (double)wF;
        double varBetween = (double)wB * (double)wF * (mB - mF) * (mB - mF);
        if (varBetween > varMax) { varMax = varBetween; threshold = t; }
    }
    return threshold;
}

EXPORT void c_enhance_contrast(unsigned char *gray, int width, int height) {
    if (!gray || width <= 0 || height <= 0) return;
    int total = width * height;
    unsigned char min_val = 255, max_val = 0;
    for (int i = 0; i < total; i++) {
        if (gray[i] < min_val) min_val = gray[i];
        if (gray[i] > max_val) max_val = gray[i];
    }
    if (max_val <= min_val) return;
    double scale = 255.0 / (double)(max_val - min_val);
    for (int i = 0; i < total; i++) {
        int val = (int)(((double)(gray[i] - min_val)) * scale);
        if (val < 0) val = 0;
        if (val > 255) val = 255;
        gray[i] = (unsigned char)val;
    }
}