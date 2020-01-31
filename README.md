# RSAT
Rising head Slug test Analysis Tool: python script for preprocessing, plotting and analysis of rising head slug tests.

## For users
The RSAT tool version 0.2.1 is the successor of the [slugtest](https://github.com/VUB-HYDR/slugtest) repository. It is developed for the calculation of the horizontal hydraulic conductivity of aquifers for data from rising head slug tests. It is an extension of the version developed by Ghysels (2018). RSAT is built with Python 3.7. It consists of a user interface to manipulate, visualize and interact with the data. The horizontal hydraulic conductivity is calculated with the Bouwer & Rice (1976) method modified for anisotropy by Zlotnik (1994) and the Hvorslev (1951) method. The guidelines of Butler (1997) are used for the selection of the optimal range of normalized heads: normalized heads in the range of 0.20-0.30 for Bouwer and Rice methods (1976) and 0.15-0.25 for de Hvorslev methods (1951).

## Bug reports
For any bug reports, please open a new [issue](https://github.com/VUB-HYDR/slugtest/issues).

## Versions
Version 0.2.1 - January 2020 

## Authors
Annabel Vaessens, Gert Ghysels.

## License
This project is licensed under the MIT License. See also the [LICENSE](https://github.com/VUB-HYDR/RSAT/blob/master/LICENSE) file.

## References
* Bouwer, H., Rice, R.C., 1976. A slug test for determining hydraulic conductivity of unconfined aquifers with completely or partially penetrating wells. Water Resour. Res. 12, 423--428. [https://doi.org/10.1029/WR012i003p00423](https://doi.org/10.1029/WR012i003p00423)
* Butler, J.J., 1997. The Design, Performance and Analysis of Slug Tests. CRC Press.
* Hvorslev, M.J., 1951. Time lag and soil permeability in groundwater observations. US Army Bull. 36.
* Zlotnik, V., 1994. Interpretation of slug and packer tests in anisotropic aquifers. Ground Water 32, 761--766. [https://doi.org/10.1111/j.1745-6584.1994.tb00917.x](https://doi.org/10.1111/j.1745-6584.1994.tb00917.x)
