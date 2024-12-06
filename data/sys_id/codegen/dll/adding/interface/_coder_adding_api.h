/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 * File: _coder_adding_api.h
 *
 * MATLAB Coder version            : 23.2
 * C/C++ source code generated on  : 10-May-2024 23:33:08
 */

#ifndef _CODER_ADDING_API_H
#define _CODER_ADDING_API_H

/* Include Files */
#include "emlrt.h"
#include "mex.h"
#include "tmwtypes.h"
#include <string.h>

/* Variable Declarations */
extern emlrtCTX emlrtRootTLSGlobal;
extern emlrtContext emlrtContextGlobal;

#ifdef __cplusplus
extern "C" {
#endif

/* Function Declarations */
real_T adding(real_T x, real_T y);

void adding_api(const mxArray *const prhs[2], const mxArray **plhs);

void adding_atexit(void);

void adding_initialize(void);

void adding_terminate(void);

void adding_xil_shutdown(void);

void adding_xil_terminate(void);

#ifdef __cplusplus
}
#endif

#endif
/*
 * File trailer for _coder_adding_api.h
 *
 * [EOF]
 */
