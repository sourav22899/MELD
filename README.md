# Memory-efficient Learned Design
**Author:** Michael Kellman (kellman at berkeley dot edu)

Computational imaging systems jointly design computation and hardware to retrieve rich information which is not traditionally accessible with standard imaging systems. Recently, critical aspects such as experimental design and image priors are being optimized through deep neural networks formed by the unrolled iterations of classical physics-based reconstructions (termed physics-based networks). However, for real-world large-scale systems, computing gradients via backpropagation restricts learning due to memory limitations of graphical processing units. In this toolbox, we implement the memory-efficient learning procedure described in [1] that exploits the reversibility of the network's layers to enable data-driven design for large-scale computational imaging. 

## Install

## Examples
We include several practical demonstrations on large-scale systems: 

* Learning experimental design for super-resolution optical microscopy (Fourier Ptychography) [2]
* Learning prior models for multi-channel parallel magnetic resonance imaging (MRI) [3]

## Basic Usage

## Custom template for your own computational imaging needs

## Requirements
* Pytorch
* Numpy

## References
[1] 

[2] Kellman, M., Bostan, E., Chen, M., & Waller, L. (2019, May). Data-Driven Design for Fourier Ptychographic Microscopy. In 2019 IEEE International Conference on Computational Photography (ICCP) (pp. 1-8). IEEE.

[3]

---

If you found this library useful in your research, please consider citing:
```
@inproceedings{kellman2019data,
  title={Data-Driven Design for Fourier Ptychographic Microscopy},
  author={Kellman, Michael and Bostan, Emrah and Chen, Michael and Waller, Laura},
  booktitle={2019 IEEE International Conference on Computational Photography (ICCP)},
  pages={1--8},
  year={2019},
  organization={IEEE}
```

If you found the Fourier Ptychographic Microscopy model useful, please consider citing:
```

```
