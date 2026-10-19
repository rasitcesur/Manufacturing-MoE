# Manufacturing-MoE Normal NORMAL — eğitim raporu

**UYARI:** Sentetik fizik simülasyonu; gerçek makine doğruluğu değildir. 

**Öğrenilebilir parametre:** 369,608
**Model parametreleri:** {"Time Transformer": 83652, "Manufacturing Energy MoE": 30354, "Manufacturing MCE": 3402, "General Robotics": 50374, "GMAW": 90334, "RSW": 55746, "TIG": 55746}

Kriterler: MAPE, WAPE, MSE, R², MAE. Eğitim raporu validation checkpoint seçimi sonrası üretilir.
Ağırlık paylaşımı yok: genel robot, GMAW, RSW ve TIG ayrı ağlar.
Eksik raporlar: Yok

| Operasyon | Bölüm | Çıktı | MAPE (%) | WAPE (%) | MSE | R² | MAE |
|---|---|---|---:|---:|---:|---:|---:|
| FDM | val | time_s | 0.16164 | 0.055077 | 0.012598 | 1 | 0.099149 |
| FDM | val | energy_Wh | 0.1072 | 0.026618 | 1.3735e-05 | 1 | 0.0030533 |
| FDM | val | material_g | 3.2906e-06 | 2.99e-06 | 3.4381e-20 | 1 | 1.5158e-10 |
| Milling | val | time_s | 0.15762 | 0.16843 | 0.00045643 | 0.99998 | 0.015845 |
| Milling | val | energy_Wh | 0.15899 | 0.11463 | 5.6451e-06 | 1 | 0.0018773 |
| Milling | val | material_g | 3.1703e-06 | 2.6658e-06 | 7.5986e-14 | 1 | 1.3365e-07 |
| Turning | val | time_s | 0.066437 | 0.068553 | 0.0012376 | 1 | 0.026769 |
| Turning | val | energy_Wh | 0.23159 | 0.20788 | 0.019874 | 0.99999 | 0.076144 |
| Turning | val | material_g | 2.7495e-06 | 1.5684e-06 | 6.8272e-11 | 1 | 6.1398e-06 |
| Drilling/Boring/Reaming/Tapping | val | time_s | 0.68521 | 0.45744 | 0.20547 | 0.99996 | 0.32537 |
| Drilling/Boring/Reaming/Tapping | val | energy_Wh | 0.36274 | 0.29639 | 0.0022832 | 0.99997 | 0.033138 |
| Drilling/Boring/Reaming/Tapping | val | material_g | 3.5523e-06 | 3.0026e-06 | 1.7716e-12 | 1 | 5.8008e-07 |
| Grinding | val | time_s | 0.22942 | 0.22999 | 0.010687 | 0.99997 | 0.079906 |
| Grinding | val | energy_Wh | 0.35295 | 0.35131 | 0.0025805 | 0.99992 | 0.03539 |
| Grinding | val | material_g | 2.8987e-06 | 2.9619e-06 | 4.3033e-15 | 1 | 4.2419e-08 |
| Sawing | val | time_s | 0.085417 | 0.093332 | 0.0099033 | 1 | 0.062698 |
| Sawing | val | energy_Wh | 0.13815 | 0.13965 | 0.0023922 | 0.99999 | 0.031411 |
| Sawing | val | material_g | 2.7806e-06 | 2.5891e-06 | 4.7835e-12 | 1 | 1.3982e-06 |
| Laser | val | time_s | 0.10524 | 0.083583 | 0.00037851 | 0.99999 | 0.013308 |
| Laser | val | energy_Wh | 0.23839 | 0.2308 | 0.021008 | 0.99996 | 0.10782 |
| Laser | val | material_g | 4.1713e-06 | 4.5961e-06 | 2.8357e-14 | 1 | 9.4381e-08 |
| Plasma | val | time_s | 0.055657 | 0.054787 | 0.00030597 | 1 | 0.0139 |
| Plasma | val | energy_Wh | 0.31185 | 0.30544 | 0.10207 | 0.99993 | 0.26207 |
| Plasma | val | material_g | 3.1541e-06 | 3.587e-06 | 4.3109e-12 | 1 | 1.1373e-06 |
| FDM | test | time_s | 0.065125 | 0.064483 | 0.022513 | 0.99998 | 0.12012 |
| FDM | test | energy_Wh | 0.033961 | 0.033057 | 2.5271e-05 | 0.99999 | 0.0039601 |
| FDM | test | material_g | 4.4547e-06 | 4.4167e-06 | 2.0714e-19 | 1 | 3.8559e-10 |
| Milling | test | time_s | 0.18186 | 0.16842 | 0.00066702 | 0.99999 | 0.01786 |
| Milling | test | energy_Wh | 0.16522 | 0.13544 | 4.7702e-06 | 1 | 0.0018638 |
| Milling | test | material_g | 2.6792e-06 | 2.7323e-06 | 1.5661e-14 | 1 | 6.9286e-08 |
| Turning | test | time_s | 0.071725 | 0.072737 | 0.0021571 | 1 | 0.031211 |
| Turning | test | energy_Wh | 0.28482 | 0.20491 | 0.014591 | 0.99999 | 0.065532 |
| Turning | test | material_g | 2.3291e-06 | 1.7421e-06 | 1.1251e-10 | 1 | 5.7641e-06 |
| Drilling/Boring/Reaming/Tapping | test | time_s | 0.84958 | 0.50834 | 0.25146 | 0.99996 | 0.38722 |
| Drilling/Boring/Reaming/Tapping | test | energy_Wh | 0.48251 | 0.34155 | 0.004426 | 0.99997 | 0.044244 |
| Drilling/Boring/Reaming/Tapping | test | material_g | 3.4755e-06 | 3.7902e-06 | 8.5775e-12 | 1 | 1.0903e-06 |
| Grinding | test | time_s | 0.25037 | 0.25417 | 0.009993 | 0.99997 | 0.079059 |
| Grinding | test | energy_Wh | 0.36428 | 0.35878 | 0.001901 | 0.99993 | 0.032066 |
| Grinding | test | material_g | 3.2523e-06 | 3.2572e-06 | 5.018e-15 | 1 | 4.3519e-08 |
| Sawing | test | time_s | 0.086941 | 0.098773 | 0.010399 | 0.99999 | 0.067202 |
| Sawing | test | energy_Wh | 0.206 | 0.18487 | 0.0036288 | 0.99998 | 0.042792 |
| Sawing | test | material_g | 3.2378e-06 | 3.3447e-06 | 8.0146e-12 | 1 | 1.8841e-06 |
| Laser | test | time_s | 0.10089 | 0.083174 | 0.00026031 | 0.99999 | 0.012132 |
| Laser | test | energy_Wh | 0.29666 | 0.28842 | 0.028929 | 0.99991 | 0.12054 |
| Laser | test | material_g | 3.8493e-06 | 3.9369e-06 | 2.1225e-14 | 1 | 8.3094e-08 |
| Plasma | test | time_s | 0.062388 | 0.061594 | 0.00029519 | 1 | 0.014576 |
| Plasma | test | energy_Wh | 0.42185 | 0.42302 | 0.21556 | 0.9998 | 0.32352 |
| Plasma | test | material_g | 4.0268e-06 | 3.6747e-06 | 2.2752e-12 | 1 | 1.0271e-06 |
| boring_horizontal | val | energy_Wh | 0.42647 | 0.44914 | 0.0035523 | 0.99995 | 0.041878 |
| boring_vertical | val | energy_Wh | 0.4041 | 0.24013 | 0.0013854 | 0.99999 | 0.029568 |
| cnc_milling | val | energy_Wh | 0.15899 | 0.11463 | 5.6451e-06 | 1 | 0.0018773 |
| cnc_turning | val | energy_Wh | 0.23159 | 0.20788 | 0.019874 | 0.99999 | 0.076144 |
| drilling_horizontal | val | energy_Wh | 0.40335 | 0.295 | 0.0024272 | 0.99998 | 0.04267 |
| drilling_vertical_old | val | energy_Wh | 0.18175 | 0.21285 | 0.0037232 | 0.99996 | 0.025702 |
| fdm | val | energy_Wh | 0.1072 | 0.026618 | 1.3735e-05 | 1 | 0.0030533 |
| grinding_surface | val | energy_Wh | 0.35295 | 0.35131 | 0.0025805 | 0.99992 | 0.03539 |
| laser_sheet | val | energy_Wh | 0.23839 | 0.2308 | 0.021008 | 0.99996 | 0.10782 |
| plasma_sheet | val | energy_Wh | 0.31185 | 0.30544 | 0.10207 | 0.99993 | 0.26207 |
| reaming_horizontal | val | energy_Wh | 0.43857 | 0.44739 | 0.0030139 | 0.99991 | 0.044395 |
| reaming_vertical | val | energy_Wh | 0.2572 | 0.23093 | 0.0014501 | 0.99996 | 0.02794 |
| sawing_band | val | energy_Wh | 0.13815 | 0.13965 | 0.0023922 | 0.99999 | 0.031411 |
| tapping_horizontal | val | energy_Wh | 0.45354 | 0.28662 | 0.0012942 | 0.99999 | 0.026707 |
| tapping_vertical | val | energy_Wh | 0.3369 | 0.26433 | 0.0014197 | 0.99994 | 0.02624 |
| boring_horizontal | test | energy_Wh | 0.45317 | 0.32066 | 0.0029434 | 0.99997 | 0.03857 |
| boring_vertical | test | energy_Wh | 0.62262 | 0.41214 | 0.011917 | 0.99996 | 0.064608 |
| cnc_milling | test | energy_Wh | 0.16522 | 0.13544 | 4.7702e-06 | 1 | 0.0018638 |
| cnc_turning | test | energy_Wh | 0.28482 | 0.20491 | 0.014591 | 0.99999 | 0.065532 |
| drilling_horizontal | test | energy_Wh | 0.57889 | 0.38124 | 0.0055623 | 0.99998 | 0.058293 |
| drilling_vertical_old | test | energy_Wh | 0.16998 | 0.15976 | 0.0025362 | 0.99999 | 0.025099 |
| fdm | test | energy_Wh | 0.033961 | 0.033057 | 2.5271e-05 | 0.99999 | 0.0039601 |
| grinding_surface | test | energy_Wh | 0.36428 | 0.35878 | 0.001901 | 0.99993 | 0.032066 |
| laser_sheet | test | energy_Wh | 0.29666 | 0.28842 | 0.028929 | 0.99991 | 0.12054 |
| plasma_sheet | test | energy_Wh | 0.42185 | 0.42302 | 0.21556 | 0.9998 | 0.32352 |
| reaming_horizontal | test | energy_Wh | 0.4968 | 0.31113 | 0.0028754 | 0.99996 | 0.034982 |
| reaming_vertical | test | energy_Wh | 0.43992 | 0.34843 | 0.0038448 | 0.99998 | 0.049617 |
| sawing_band | test | energy_Wh | 0.206 | 0.18487 | 0.0036288 | 0.99998 | 0.042792 |
| tapping_horizontal | test | energy_Wh | 0.63671 | 0.49504 | 0.0031747 | 0.99991 | 0.044901 |
| tapping_vertical | test | energy_Wh | 0.46196 | 0.36527 | 0.0025544 | 0.99995 | 0.037884 |
| General Robotics | train | duration_s | 0.14833 | 0.088237 | 1.3718e-05 | 1 | 0.002704 |
| General Robotics | train | energy_Wh | 0.17266 | 0.0746 | 0.0003849 | 1 | 0.0059034 |
| General Robotics | train | cold_energy_Wh | 8.6672 | 12.273 | 14.817 | 0.97711 | 0.97122 |
| General Robotics | val | duration_s | 0.16108 | 0.090155 | 1.4718e-05 | 1 | 0.0027845 |
| General Robotics | val | energy_Wh | 0.19348 | 0.077353 | 0.00041859 | 1 | 0.0061714 |
| General Robotics | val | cold_energy_Wh | 8.5884 | 11.934 | 12.145 | 0.9815 | 0.95209 |
| General Robotics | test | duration_s | 0.15661 | 0.088757 | 1.4098e-05 | 1 | 0.0027372 |
| General Robotics | test | energy_Wh | 0.19194 | 0.081183 | 0.0003839 | 1 | 0.0060063 |
| General Robotics | test | cold_energy_Wh | 8.7929 | 12.529 | 12.533 | 0.97496 | 0.92693 |
| General Robotics | ood | duration_s | 0.14659 | 0.094456 | 1.4412e-05 | 1 | 0.0028174 |
| General Robotics | ood | energy_Wh | 0.18269 | 0.078443 | 0.001564 | 1 | 0.012385 |
| General Robotics | ood | cold_energy_Wh | 9.7698 | 14.865 | 67.164 | 0.97073 | 2.3471 |
| RSW | train | time_s | 0 | 0 | 0 | 1 | 0 |
| RSW | train | energy_Wh | 0.19864 | 0.18607 | 0.00040725 | 0.99999 | 0.014696 |
| RSW | train | material_added_g | — | — | 0 | — | 0 |
| RSW | train | wire_consumed_g | — | — | 0 | — | 0 |
| RSW | train | gas_consumed_L | — | — | 0 | — | 0 |
| RSW | train | spot_count | 0 | 0 | 0 | 1 | 0 |
| RSW | train | physics_prior_energy | 1.3592 | 1.1182 | 0.011359 | 0.99965 | 0.088315 |
| RSW | train | history_zeroed_residual_energy | 1.3448 | 1.1075 | 0.010971 | 0.99966 | 0.087472 |
| RSW | val | time_s | 0 | 0 | 0 | 1 | 0 |
| RSW | val | energy_Wh | 0.41729 | 0.34267 | 0.001443 | 0.99996 | 0.027764 |
| RSW | val | material_added_g | — | — | 0 | — | 0 |
| RSW | val | wire_consumed_g | — | — | 0 | — | 0 |
| RSW | val | gas_consumed_L | — | — | 0 | — | 0 |
| RSW | val | spot_count | 0 | 0 | 0 | 1 | 0 |
| RSW | val | physics_prior_energy | 1.3465 | 1.0629 | 0.010959 | 0.99968 | 0.08612 |
| RSW | val | history_zeroed_residual_energy | 1.341 | 1.0513 | 0.010933 | 0.99968 | 0.085182 |
| RSW | test | time_s | 0 | 0 | 0 | 1 | 0 |
| RSW | test | energy_Wh | 0.44547 | 0.37128 | 0.0014687 | 0.99994 | 0.02916 |
| RSW | test | material_added_g | — | — | 0 | — | 0 |
| RSW | test | wire_consumed_g | — | — | 0 | — | 0 |
| RSW | test | gas_consumed_L | — | — | 0 | — | 0 |
| RSW | test | spot_count | 0 | 0 | 0 | 1 | 0 |
| RSW | test | physics_prior_energy | 1.2917 | 1.0601 | 0.01065 | 0.99958 | 0.083255 |
| RSW | test | history_zeroed_residual_energy | 1.3044 | 1.094 | 0.011555 | 0.99955 | 0.085922 |
| RSW | ood | time_s | 0 | 0 | 0 | 1 | 0 |
| RSW | ood | energy_Wh | 1.9752 | 1.7309 | 0.055635 | 0.99892 | 0.21681 |
| RSW | ood | material_added_g | — | — | 0 | — | 0 |
| RSW | ood | wire_consumed_g | — | — | 0 | — | 0 |
| RSW | ood | gas_consumed_L | — | — | 0 | — | 0 |
| RSW | ood | spot_count | 0 | 0 | 0 | 1 | 0 |
| RSW | ood | physics_prior_energy | 4.1141 | 3.4822 | 0.21462 | 0.99585 | 0.43617 |
| RSW | ood | history_zeroed_residual_energy | 4.2099 | 3.558 | 0.22489 | 0.99565 | 0.44567 |
| TIG | train | time_s | 0 | 0 | 0 | 1 | 0 |
| TIG | train | energy_Wh | 0.23836 | 0.22814 | 1.2264 | 0.99997 | 0.74677 |
| TIG | train | material_added_g | 2.0057 | 2.0443 | 1.4659 | 0.99926 | 0.65756 |
| TIG | train | wire_consumed_g | 0 | 0 | 0 | 1 | 0 |
| TIG | train | gas_consumed_L | 0 | 0 | 0 | 1 | 0 |
| TIG | train | spot_count | — | — | 0 | — | 0 |
| TIG | train | physics_prior_energy | 0.45562 | 0.41449 | 3.6113 | 0.99992 | 1.3567 |
| TIG | train | history_zeroed_residual_energy | 0.445 | 0.40869 | 3.5205 | 0.99993 | 1.3377 |
| TIG | val | time_s | 0 | 0 | 0 | 1 | 0 |
| TIG | val | energy_Wh | 0.24895 | 0.21974 | 1.0032 | 0.99998 | 0.71041 |
| TIG | val | material_added_g | 1.9482 | 2.0877 | 2.0547 | 0.9992 | 0.75205 |
| TIG | val | wire_consumed_g | 0 | 0 | 0 | 1 | 0 |
| TIG | val | gas_consumed_L | 0 | 0 | 0 | 1 | 0 |
| TIG | val | spot_count | — | — | 0 | — | 0 |
| TIG | val | physics_prior_energy | 0.40066 | 0.34437 | 2.0596 | 0.99995 | 1.1133 |
| TIG | val | history_zeroed_residual_energy | 0.40817 | 0.35332 | 2.1455 | 0.99995 | 1.1423 |
| TIG | test | time_s | 0 | 0 | 0 | 1 | 0 |
| TIG | test | energy_Wh | 0.28526 | 0.26343 | 1.4986 | 0.99997 | 0.8402 |
| TIG | test | material_added_g | 2.0981 | 2.079 | 1.0987 | 0.99925 | 0.56727 |
| TIG | test | wire_consumed_g | 0 | 0 | 0 | 1 | 0 |
| TIG | test | gas_consumed_L | 0 | 0 | 0 | 1 | 0 |
| TIG | test | spot_count | — | — | 0 | — | 0 |
| TIG | test | physics_prior_energy | 0.45707 | 0.41453 | 3.6979 | 0.99992 | 1.3221 |
| TIG | test | history_zeroed_residual_energy | 0.46807 | 0.43046 | 3.8937 | 0.99992 | 1.3729 |
| TIG | ood | time_s | 0 | 0 | 0 | 1 | 0 |
| TIG | ood | energy_Wh | 0.91028 | 0.79118 | 38.832 | 0.99987 | 4.9872 |
| TIG | ood | material_added_g | 6.7115 | 6.604 | 17.398 | 0.99449 | 2.2291 |
| TIG | ood | wire_consumed_g | 0 | 0 | 0 | 1 | 0 |
| TIG | ood | gas_consumed_L | 0 | 0 | 0 | 1 | 0 |
| TIG | ood | spot_count | — | — | 0 | — | 0 |
| TIG | ood | physics_prior_energy | 1.4383 | 1.189 | 85.34 | 0.99972 | 7.4948 |
| TIG | ood | history_zeroed_residual_energy | 1.4019 | 1.0713 | 69.414 | 0.99977 | 6.7529 |
