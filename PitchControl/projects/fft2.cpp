#include "fft2.h"
#include "math.h"
#include <complex>

#define PI 3.14159265

void fft(double* inputs, int N, int s, std::complex<double>* bins){
    std::complex<double> i = std::complex<double>(0.0,1.0);
    std::complex<double> t;
    if (N==1){
        bins[0] = inputs[0];
    }
    else {
        fft(inputs, N/2, 2*s, bins);
        fft(inputs + s, N/2, 2*s, bins + N/2);

        for(int k=0; k < N/2; k++){
            t = bins[k];
            bins[k] = t + std::exp(-2*PI*i*(k*1.0)/(N*1.0));
            bins[k + N/2] = t - std::exp(-2*PI*i*(k*1.0)/(N*1.0));
        }

    }
}
