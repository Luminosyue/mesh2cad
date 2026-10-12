"""Standalone mesh-derived CAD code, with embedded vertex and triangle data.

This reconstructs a faceted BREP, not an inferred sketch/extrusion feature tree.
Original numeric coordinates are retained; physical STL units are unknown.
Open meshes remain CAD surfaces. No guessed closures or thickness are added.
Run: python part_XXX_cad.py [--output-directory PATH] [--no-validate]
"""
from pathlib import Path
import argparse,base64,io,json,time,zlib
import numpy as np
import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4af3caebbad24f25a04e4db48a85b74d/part_007.stl', 'relative_path': '4af3caebbad24f25a04e4db48a85b74d/part_007.stl', 'source_sha256': '1c39a3b24b6ab44ab80c7794359d2d76beacc7715537f4ba8d731fe9c955711b', 'input_faces': 270, 'input_vertices': 233, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.11918219923973083, -0.22104445099830627, 0.03984621912240982], [0.2261120080947876, -0.1755388081073761, 0.3081333041191101]]}
GEOMETRY_BASE85 = 'c$}r032+rv7KSg|AP5Ws5+#tl1VUKCVgeXh8^{O}K(??iFF+z;F(CnDPX}ZPAd4CxfaI|+vPgomh|tJRSVRy-L|Q?JfM~QF0Trju{r@-8Q!`alGq38e^SwVO=bn4I`}Ip#y2KVMUP<8<q9*r>4(wf7DNz|!NsUWL9g{R9A+7$)DHDpQ^4gb|Kfcj9u2YvjMbtPoDST)`+K|-nrk?QTiP7N^p76xv)G?{?FAqvi9hxBi^YJ6o5*$BmSbR!?^S)MOR8)i~s&<5DisyfPm3CS%_e|U0%86Fz>|+Nc#_m}w@6FlS+Bd_};U~3Or{BNvF7oM{XYOd<Sdj0kV}6>pUgy`jfI6EF!Oz&NebwEDZw)*lzDjz0gML4!0DfSm_Klsb;J5fz`$mbz$ZrK--Fk@pm^H|+dII@n)B&CUMHTH^1CAp<9KN*_eHwcb^?udgD{J3O#=eYCzt_I8sLFvy>sz6tH|pQd3xv=5#?Tb)8{TIQJlelyJkY*bF%mxeH}damUloZ$KU~*pwoK1cb!-Zs^Rb?+ze&IUt-Y&%D<%YUwg#Yn=|QM}aX03CF9Ci6`w96D{@aO|&x`D5%N^9|H5vKyv0pQD9OgE03i4|PV*dGKwQoIK;>tG`24M~%+3=ZfovVhqo!;i^M{V1HIb>{y&wi|E_~xEn*sp(I(=Vg`_^c1LUnB68&i^GePu_cDmTTWUx#_5`UpE+j`g-jfSsiq~@8DeRtGq4n%Z*3=j#=9G1eH64pR@j)^SL_jRz>Ywy*DF&|5^B9!SJicqJEF&x{f_6MEk}e)G@!lt@G{PVcIuWaNU?_^wTsP>n5ST^<;t0_Z6>)Iyai3pU5cmStSbVZkwU=?ZyqX?+a@T{}k4>KdYyGtFS57O+|fAnL1ea>o1P$pFiIZb1oBkPOo>**1oDa6aM^Y?VDY{(!S9*Qv1Gi_|}En+BYZV;QVR!g7#J79n`51fa6;ozA@@2*Sc1R9@_VQcHdP;%^0YCU(y3t9b*)HHLJu4oS*2^TR8>wZTKepv`WG^@0HTNYS+(yo+H0VIr!eo`ug%bn1FSku7Elniyzl@CYjo|Q{h|YJIEgeUqx3$ouqpwbw3klVcjkP=rb-PU+4e!8s@eMzL|Mi=bPWbH_rv4&LZ^bdnX)yF06)i-wf9M7?oc~e)S;KiOxbl4;P{S&0wsXg8BF&>!Z)s9^|jZd{hnkbwg4At>(H<-=>vVcOQJC(N5i`wFtg%UJdx1n-#qR$MH~Y*BsQIO{jCY4(cDl@wKnEM4!LZaqY`aU5|am)kXdOIPU5=@;!6mTimbJm-+P@y88G0l!xPWprNaO?`8N_|47%IJ>TQ}G&eSJ9d}iHH}Z=-i~I~6ckj=;Q2$u8YhT{lIG;Uzo^$nYJ^|kjXy%%m_m%yaPh0q=|2$c882zk(Z~4!Y+3<b2tx$(^_La^@{<s*_;c>V2CZPYb@GTy9&ldQqpgrnv4tBkf$p4`u{LSdoT$zl0mFkK*i!mRM2iK8zFnpDd`It|@H^aN3P9FOVnu2wWp6D|N`!#*jF^6pU)_LsLUIgDt?~nRdah~}0;`&k*2OxhM&IfZfue&Po$S=V8pgO;aI&Z@_r{a9@G=cA#JOn=X>$!sK$j%++>facUgFbI2x%x2zaQ^!y4u?OT*W(|{(PvPys~>X-t_$z>WLG~{I()TstZUBRja#v9A$)^#wzA=SOHOq4Zw2neek0*q{y8_>i~956s|%cS1bolxsi?#Ks_ho?J1#<<Hj7c`srDc1J_cu@PUu1S%Q|b{_W^uk$O!mz;d@IjhTkd_$E#~Q<a?H(eo!a)=R0ZNo&aBUzmNOfVfvr@Q0JA;@p;wAt9{SNRmd;bP5X9L`oFG)|I#oVmyChhH|MXzx~0FweK`rf@#zNFem%X0BR^{k=EMFy3zOh~xeY%1@k|{HKY6>WA8#Uj>tU{|AM0eA_SNfou6}&E^b7a6=IjfdiTWM)VqMPJsz`tEe&n}B|5nyK_}llp=4|zwfqou4;F`0i6MPkN$hBYV%v{uI_7U=5Lw$Q+3)Ja)0mo$|`m|fdpw3qK=2rA+H=zH3ekSVMKR1V8{u1va=+l0sE!ItfZ@h&*jU@UfucFRD%wJuKgWu0aes9d*I7t82HTXL)e>1EH)}4AC>&9XJ-m>tmqc>dp_5L~t`7>_w^BMhn8__@W9enm<hK_(g=&q|Dt2BJ$ZlS9mmCW-h<40FNc2D~DJ=dJou}P@k{65y@oYijn-F`<t`&Uh;!O!{KHD{%eZ`}LcHD_<(M66rB=*dU-tI{%1C!(_Ujp6v*u+Nu2uYD^3`GrUDch=Oh+BajWXy5FK&m~`60Q|S$TXXQaq}st(7X!7g&i#NosuJ>_sfs!kmcuWsi2UF%)LDtoTccPl?HljFHyiW&!0mADTb;wvf6dbPyj>QCIyQXuL58mHn+D(572(>iSs@C3Y<<^$?R^c<XJ{1a<na4d#}-&OFUr-A-3Y$ftucJ|qpmlFf32~rAI~ZH#`%_5*FVoIosl2W3i)$6&$IAVg5jE{cXll5ScYq!-U;x{Hf`Z^zp85-{EIQJ{d#}xiaKRtQ9mRe-`iscat<$IZfYLBFP$EWIZT0XwQhp%OZ(xQfpJ)OC)V|h{|o%>JyE~;Q5=`hV%S%sKB(iv9Mpp{@Lz+kJ~_?fPX7<)$F0Nn<cVWZe_>zrd8aDAM-8TbgnnQlJ~!5uLY<I)sM8;F^JT#|m&7BVbFec__~nM8pKp0SY^a7g<iNMm`F&ske4}L|=8%H(!D<<ZI%nY<C8yzhs|nvKI?S~%&*3@f^G*0B_vPIJ-&#MyHD~)hTrXDBQLZ@~@w_f7q+(t6uL>j4=bBVk|HdWw=8iPf=W#dVR=_Va#(mtMhp*bu=YEaZ4dI_3<Jzy8LcjWW*PPActI_|5Q_%k^o)6PvkY9Bw^8M#S8ho=yy6gB_5v@^Yd%ElRTGimI$Z7C7H}B6K;2)jtnwyo=4t0LbMEw!y)AxOM&T~HI(*g6bM)$=$N5NO~n(#b?Z{A%B--qLC2aP}-GaGf9RKsyENq?3PKG!wsk3;<**SqSN!+3s9-++Cwj;{-RwJH}r`?T*bg8y5tt55qDe6zwX*Shw|rTjeUdkXdNe8xJOgMP+&wQoI*=On%lS7L5^hHKw!$mcU-c4OU{DcUzK;`xu6u?zJJK8D`_&u7frb9vk^!QY7b-kZEGj@#(xM?7y)YcjF!plj%7KcDAhuSNYUH&ACUp2JvcW~0ux1@J#(en<FL-EYzVP&|h*)~`YS=-XKLEcdl68~(d@;ZH@rx6ds2Eeg@k82G*o&OE!go=R8p1^!a2tWu&<s**~Kf8>$0nDX++fB#52snLJ;Nc!1^|L-H|ET@Ml(g))N@*Cs@jA`Tr<V?nw$(iI=8Ap*{B~NEeCQF<_ULkXokyFC^7}t~ckq<L&CLbo}Gj1j4lg}`2BA+3jWL!r+Nj}7wLq0@)pK&?)eezDmZ1PTWF5?RF3hqt#BS)V&I!6hgr-Uz3!k<yXpHsq@DB({j;R}@T$BZA5cR1SXXcr}HQNl+l;S-eb5lZ*~CHx*G{0=3&opA>_&(VjDc2mM1P{PM3;Zv0GSxWdcC48I`-cJedVay}1bhOsdYD#z`CA@_a-bM+(O$l$HgjZ3*Z&AX_7*~>KI-2ij79~8F5?(|JFQ$Z-Qo>6p;nykQd6e*M#+l?)N8=rhql70@!WoqCG)mZ{geOtLV=3X$lyC}TD!G@Vct^b{;Q^HJ5K8zZN;ruU9!3cdrGy7k!hINfk)s{8b<~m)Zchn!qJ+Cp!W}8$=PBV9l<>2Za1+L8a&t$qj#^Q|f1`vuQ^Gwc;hvOm93}iBCESh@HW-_e>p5!Zr~xG$NeMTigd0=BQIzmAlyH4YID!(c%UF-x*U?}{{V3r<lyCwiJe(39NePdjgcB)YFD2Zcu`juqqZmhRDB%v2a5qZ0J0;we5`KXaZcPa{rG%ejY(|!Q(rfC^`<Jl)9w+R-4+{J5mBLw+@SBwILP~fJB|L+1I$7?CuQ(b*2~VVir&7Y{l<*WvcmgGyMhU-636Ek-Cd)nPp!)OvCG5Y)3H$GZ!v1@uu>XE4?7!y<`|r!b{(HCZyNtPHxhJksxX=5@>nY*Ql<-zccoQYOjuOtHgqKso*^Dd59!EirzF@3I{*v(uC489@4rZ)I4klNpghLpE$RXrVMh`iZ9LD$sIgD&S(vwXIf5Ui%{0;eQ#>?cd$yXVJ$-(UPDkc0CB^*u(*I*1Ghp_J&lyFVPFmg?DEk>JMi+qg|E@1qI{0;jqpoDKQUL{{;uQw>+>x|*#>*U&uHOMvCUu{ab4r48HE%sN3628e;KrZ0gHyN*!ue0t={_ah_FRA1Y0i~X#gaa7Mk^{(3GyawQG&zv*334F0Dq}fvRdN-^GUO`crx+h2KSi$0_!n|zawWzR<Vxg<j3vn>xi?{X6>(IW5`LVqDEV=6dB$So^5hDP#mQY_ixjO?>_7eM&z~<-7IFO}(7*ns`_HpSe{-=@>z{wDb%`w@`*xZus=xT$mn%X21DnInfd'

def decode_geometry():
    with np.load(io.BytesIO(zlib.decompress(base64.b85decode(GEOMETRY_BASE85)))) as data:
        return data['vertices'],data['faces']

def build():
    vertices,faces=decode_geometry()
    center=(vertices.min(axis=0)+vertices.max(axis=0))/2
    extent=float(np.ptp(vertices,axis=0).max())
    if extent<=0: raise ValueError('Source has zero extent')
    construction_scale=100.0/extent
    v=(vertices-center)*construction_scale
    sewing=BRepBuilderAPI_Sewing(1e-7,True,True,True,False)
    planar_faces=[]
    skipped=[]
    for index,tri in enumerate(faces):
        points=v[tri]
        if np.linalg.norm(np.cross(points[1]-points[0],points[2]-points[0]))<=1e-12:
            skipped.append(index)
            continue
        wire=cq.Wire.makePolygon([cq.Vector(*p) for p in points],close=True)
        face=cq.Face.makeFromWires(wire)
        planar_faces.append(face)
        sewing.Add(face.wrapped)
    if not planar_faces: raise ValueError('No non-degenerate triangles')
    sewing.Perform()
    shape=cq.Shape.cast(sewing.SewedShape())
    representation='faceted_surface'
    if SOURCE_INFO['input_watertight']:
        solids=[]
        for shell in shape.Shells():
            solid=cq.Solid.makeSolid(shell)
            if solid.Volume()<0: solid=cq.Shape.cast(solid.wrapped.Reversed())
            solids.append(solid)
        if solids:
            candidate=solids[0] if len(solids)==1 else cq.Compound.makeCompound(solids)
            if candidate.isValid() and len(candidate.Faces())==len(planar_faces):
                shape=candidate
                representation='faceted_solid'
    if not shape.isValid():
        # Explicitly represent troublesome nonmanifold edges as separate faces.
        shape=cq.Compound.makeCompound(planar_faces)
        representation='independent_faces'
    shape=shape.scale(1/construction_scale).translate(tuple(center))
    return shape,{'representation':representation,'degenerate_faces_skipped':skipped,
                  'construction_scale':construction_scale,
                  'sewing_tolerance_original_units':1e-7/construction_scale}

def describe(shape):
    b=shape.BoundingBox()
    return {'valid':bool(shape.isValid()),'solids':len(shape.Solids()),
            'shells':len(shape.Shells()),'faces':len(shape.Faces()),
            'bounds':[[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]],
            'solid_volume':float(shape.Volume()) if shape.Solids() else None}

def export(out,validate=True):
    start=time.time();out=Path(out);out.mkdir(parents=True,exist_ok=True)
    shape,metadata=build()
    state=describe(shape)
    if not state['valid']: raise RuntimeError('Constructed BREP is invalid')
    shape.exportBrep(str(out/(PART_NAME+'.brep')))
    shape.exportStep(str(out/(PART_NAME+'.step')))
    report={**SOURCE_INFO,**metadata,'cad':state,'step_unit':'mm',
            'source_physical_unit':'unknown','coordinate_policy':'preserve original numeric coordinates',
            'code_kind':'standalone embedded faceted geometry','source_modified':False}
    if validate:
        reopened=cq.importers.importStep(str(out/(PART_NAME+'.step'))).val()
        report['step_reimport']=describe(reopened)
        if not report['step_reimport']['valid']: raise RuntimeError('Reimported STEP is invalid')
        if report['step_reimport']['faces']!=state['faces']:
            raise RuntimeError('STEP transfer changed the face count')
        error=float(np.max(np.abs(np.asarray(report['step_reimport']['bounds'])-np.asarray(state['bounds']))))
        report['roundtrip_bounds_max_error']=error
        if error>max(float(np.ptp(decode_geometry()[0],axis=0).max())*1e-5,1e-6):
            raise RuntimeError('STEP transfer changed bounding dimensions')
    report['seconds']=time.time()-start
    report['status']='SUCCESS'
    (out/(PART_NAME+'_report.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-directory',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--no-validate',action='store_true')
    args=parser.parse_args()
    print(json.dumps(export(args.output_directory,not args.no_validate)),flush=True)
