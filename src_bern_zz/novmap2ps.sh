#!/bin/bash
cat dict.ps 
echo "gsave"
echo "map_width map_height scale" 
echo "/img_width " `awk 'END{print NF / 2}' < $1` " def"
echo "/img_height " `awk 'END{print NR}' < $1` " def"
echo "/scanline img_width 3 mul string def" 
echo "img_width img_height 8"
echo "[ img_width 0 0 img_height 0 0 ]"
echo "{ currentfile scanline readhexstring pop } false 3 colorimage"
awk '{for(i=1;i<=NF;i+=2){if ($(i+1)==-4) col="000000"; else if (($(i+1)==-5) || ($(i+1)==-3)) col="ffffff"; else if($(i+1)==-1) col="00ffff"; else if($(i+1)==-2) col="cc00ff"; else if($(i+1)>=2) col="ffff00"; else if($i<0.45) col="00ff00"; else if($i<0.95) col="ff0000"; else col="0000ff"; printf("%s", col);} printf("\n");}' < $1
echo "grestore"
cat end.ps
#ps2pdf map1.ps
#
#                           -1 - 2 ������ᨬ� �����
#                           -2 - �㯥௮���� ������ᨬ�� ����
#                           -3 - undef
#                           -4 - ������騨 ���������
#                           -5 - 堮�
#                           0 - ��ମ����
#                           n > 0 - ����� ����ઠ樨 
