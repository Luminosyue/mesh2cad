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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f0742330720b49e59740835a12380219/part_006.stl', 'relative_path': 'f0742330720b49e59740835a12380219/part_006.stl', 'source_sha256': 'ae15ec9561c39c3330539db40ad65a39ae13ddd42524627b786c4b7faab99272', 'input_faces': 408, 'input_vertices': 257, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.173336923122406, -0.17837877571582794, -0.13910092413425446], [0.1733357310295105, 0.08874887228012085, 0.4999997019767761]]}
GEOMETRY_BASE85 = 'c$}r033N@@8pk)HC~Ang!X+X#&w{qxm^DSTJVR2hCQ;NFb4{m8y&76W6%Tb$5tI@l5h7Ox^AIJ54BSX1G?Ew+LkREe{r%6q=WO0uZ@qV|Z~cGyXWxCkv(KK+4qu-VE>#$P>an?({Ku}V!5EKntO}bR6g+iIK+u%t6DG|n#wrS*e>7d)Z%|*~p~cvAHrq2WXi7k^XD5^AN25A;HZ^&UnixDac;ti;6N3YTxZiW+xG6!ZKV|gDNkQt*AGB`g)zs9cQB%`g)BpH+S4~05YH=b)RohSNwsK`(+iYA-E1C;m$=M`)TiHV~dY_%?I<*VeCZQ2rtsR;P-~Q3n1g@6!BvFs%+u$qD>@fzv-5pVmEld<@PH$rHZ69Ba(figu4G)N)8=kej)n9N{l()2QM0xI5dsOHpuXvuPJ=v4;WP8PZDTOzZ^*%cl5yF2~N_!Z}v+rVsZ~EzOgx*)Y&mR>2%IhK@&9}j4Lo%t|ntD+Av<zyOs?9|Gns4q!`P;h9Ow#*oe4BmzXY<YsV?FP;7rw3IHEO3T?&LppBfp@As9*Cf+fBk}d8HM-ZyV@N^-sSp?#nW_KDFndO!2(f{fxPK-|n45&uc~0JiV{D=0%J8%AGaTV{6f7hq&HzdhQN?d50bP{2lc_q5PGkPMbtKd(@-+UG7mn>FYP@ePy;^tY|-%fJD7-dh(e1N81TWdf&W0m-1h7(NK?lTj<uem1mX5O%eHQND=uv{KL2D`BqsuU;O?;UAixi*2jeU1t#i!wy2+YzAQEDmZ5xwj>5N;3Nn;eN>Kl_jA|TjsHdT~$j5^5;;83cyU53~w5*}LS<7=<EzzEAMjfiB;zMfBIYCK!-}ZA`(Vq4%PDL2X7k3rUOL;mhQSU3L-{w!{t##dy=UR~`8|Rl~@PCOD^M)<DiOADjvnJIOQT({LzWXlGKKA3)sr-^$nrHg^i|d+Pt5TkxeQ3N4ND<@Ldc>9dygX``-)|cIrI_C~4Hos711nQMIs1azA#Up}gTFq7{8G0?J+=?a#*21o5iRnxk83XSxBOK``0SnfaY8SesUI#YEqrr$1L50;w~rM0-z+J7Tge~k{({Gd`mEo(P(9^VQF{!SMdLzYblr9{=swowQ~$YCB<i(PI#2af9Y*uUH!p>6bxR_DP@2e}B@_tXyf+Tdq22;f&-i@u1J2NO>)riT_<_Y@X`ItIwMU(&{!pHg@1I8V9_BG?_$#`PkPMpVy#mGfG7T>hzNuP)@Xh5jsXgC$N#(V9ra{15y>E`Ber4`?i{>}@?5jKE2j<dz@<$=n-)kGq=OJH+_Sby#z2YK&(`UmCK0DS@%ro}fG+WGDe1`h%gP&9Vo8H?dbly3e-e=p_iT-KM$)R-tzIkzxSTD?LQw`-cU#s83o{^7vNvRwq+D-Eru4`*`!BC!MRj2Fb4y5t8^9hZg2YH71S@W&)T*Y`%?nH|IV;xX{_Q|Gsve`a^Z{PJSOnmRgSkbS{g^%gFVcFt&*-W9g^uBpdcbYc}X`E`l5`*?U(<a_f&*E;vx9m+2?PlBhNcfh%1(eUu)MUNSmSxhqd3AJ>-nY$&qx}iHX((^rQeHfF=38;Tp`O2bQ$Azsh;`87^N{k~T1Cv;*8CxfdY>I^L-X_SNa`n&ulVkc(fg+8NRf}VG3Dtf{~pbUN@U(f!*yR*raXfS4L)1#LwWY~-K6(zy-SA+|F?r8f0my|_d7C|#@*#nNqXNF_KNyd;8E%qT6w=B8dv@YVhp}ZD_W=WOB?Ig{1B`o@a^%XY2RgO7_awDy=gpJFh6KMD~EMqAUzk&S3=5*`%*kZME%OfT<Q<AUr~P>eMID``RuX>%|rQ7qW_qB<iLL|%3H@`9}C~Iy@|-v+LgwOH7A>{>yt|R7OZ!ctSlNY2R4g+qjkS~yxuqYy%6KVuI-oLYwI$@KF#6hV4QkQO464%-=%rUJiimQ&x%Yczs{Z7v&ZFRy>ESVoz|~9wBK-)$91jPM>+iJcWFPcB^vwlJCwiI1)3+bD{RvH))?xy%9?O$&-4tc$1`D?$P?q&(mI{`Rj-FMPKVW}ee$Br<6Yj8zr&aEbof%9=CmyGrFPSNx!vrYa;UuY+%2neg)jFX`@KBj%i}`x<$h@Ken|Dp^8oxe#yfm@oLbjCB43)XOb;GY{nEUu`SSd!^eUiskmhasuTO+8&-3OdPpN)sy|DFtPWemgn&!*vmw9_3u4`ORHD6v&m6tClA8CEpe0hD>e0hCm1B)n6Y5$<?ens_5`wdot#R`@7CzgQxI8m>(&#^}pkT30vOp{&;U*1PqP8JDY-gnvSycWLVH+iRM-znE<y_?RcpUV5U^Tp!z&rvCOZtyKz)Ax(=uU-qEd6b}e;*;!Pk=N3FG(I)|T<St`-9Puyd&C?U@}>PGyHb+g3#I+1Z9!?uN7}DyzBQEIk1Y4X4drc{X`Qv_9X9wZ;Rf~F-OG*TN4Gd6>Wlu;c-?7U!e^gOqyCm$hU$^_)eiq$51L1#*B{rHw`uLRqEm{#yy9KKD(X4yY4FVrs)^^tPK469XhrW&@;+blm4Ipc#rKq3M*qq#%0IN@JiX7lL<(Q2)soiDAIj19Tn34JtfLZW-msUacE&k|slo-CmoqC-o-4ws{>(7iXKtYPd-GVd=dvuy<GCB@oXMg;*dOhu{lKuwCq%!N-gg|n^uD9)cNM<;KIQPG_bFDUD*4iTnJuEa@ZWfkt58$;@_V19svDJ;-X9&l^!{icSBHG*eOB`oZQU&6x5-dmdY^Tam)>VB@pb9Gr1xTnFTL+;zWl!LC@;P5JN(}C+}V9vmz~$WO!@bms_1?Be86#C>3qOZk90nu`SSUI{r!5vf8)Fb{u}2l@ZUIZf&a#N3w*nFzcr4|H~8{74E#6FVKiSlhcQj5FMRp@O7rFOE6tbBuQXpizjFA}`IV!7>HNxi#+~Yy&gC>;K9|#c`CN|G_n>;D^Fz&-&kr?UK0kESBb^^wW;LYiMl#wz9HIAp%~#6qq4(BOG>$Z%HHapEXdgOPO!TC7kj_^%Up`-T_|o~R=F8`(<_{WCdFfnN^X2nccC883Bb_H}zI>kihL7`P&1X&jCHBLt>+Lz>dd-{B{YvNFnlGPwJACQfTk~0M+HWgI`_X>p`{wj~73}LWy2a~#`F!3{-fyPxO|3H`^yTGqdnK&}<)c6U_ci=gWA*OmYpkwnlc-UKRbit>>i(p`P5#mJ?SIl3)AqmmlSbQ?9sb`xX?UnPxT{eS!MTna?bK+gMtf)*aC>lLXdQ54up87J>;|p?Ed#CqZUU_VZUU|itqZOVt_H0Rt_F62z5{jvmq2hX2`vpS2`&XK1}+6=(0a`I;p_>m3HAinf>r|80#|1I7?AWmXeID_;QG)i;QHW3(D%VytAZPWo2l^u)D>D4><TUmEeGaW9L%)^xGA(1v;~-JLonC2;O0;hv@Mvc2bgO`@Vn5~(28KLb--NPfLntbKwE-4tMRcKqY<2kKs$hkfEPf$zze{^(2n3>a5tzK+zs3V+6CMLJQ?~Scrthjf^#QE{gA5*^h4(CtDLJryD(?p=3E<UX3nv|xe2r*bB-O(6`)?sIo3G4K|3(#*yP+8`Z05kWzOxPotbm&b8d&={E-@iq1~aK!JYAJIL}ujPz^<m3DCaKKyY7h5Q6h?1m}s+`QVA*Icj_j9S5Bc9tWNQRlqaA<8?WWM{u61#y_CFp%cKp!QVprg1-fOLxaHH;9&^PqY#`&K!<}zfPE00`$H#!`-5jf=YVH|2k6>m0D|+EYK(<`4*eSZIoKCE4(tn_2Au((2A&Qb51tOTK&OH&V1Hfv`Xe~|sWDKEL2Ar~`hopWW;TNJ7YNP)(B9wx@GJ!9&!FFeKLhtcaQ+7B4gLl^6gmt%6x<cTc^-5Wcpi8Xg7a6<5#X=Dy`VneUf`Yx&YwX0gFgZHgU$r^1J8vH0M7+~3jGrNDR?Av_K%SW&SMzOV_YXg$1>+!$GHdebLN~IId_BlGUr^%IT$*PIp<!^3!u}PbFSt*1ZrW<xt;T9s6TVA1)RG>{lMM9gQ0`K$!gqEBVUa$HIArJ0R0_Y0Op$kt~<ayIA4ah2YeZP8@d;K8~nE#kD-4+_k#Zb{|mu+9dr+P9rzdM4)8DFh0x!@3&CrkN5E^q%MhHGK*PXG!2d*W-lfJfXdyHV9ESGdd_|43YD7bif}_E|A~-LC9tJN0FNH>emx6zU?gRe_-hg)7fVSKKUu)ZaX#2<DhtNpyLvR}OFgOjI1U(8qihJXnr^a7uY=cICw}BTUIIqOLuS9#Sgs-(v1llhGb#Y#+#?NYmLqoyg;4{#8@M3&t8#G*(PdM@oM_JC_tFc^-W6&t@G4Kg!3ixMyClq=N914zyo&f)(#&>EQgdPAN1m{BIz{~NSDCj|O6gUN%3%-EwhCmO1L%^${-+?dScL~t#-~@0Cg7a@`tbne9ZU?UduZD(zbJV!6##87E@Kf+51n1L;S8608IA^PIQH_^s#3DHV3C#v)qx_!;&L<I^UqerWPvg3;5u6`D?}Ia;8PNOS`?$9Z1m`<y+=He=bHM4~ROnN1D!2%G30wqz!f0ORnhd=JzJz;7h9-iO!M6~cZ$PubH^6r2ORydM2zn9x2z(xT7knOkU5(?=IOtvG?8jVFpm)J{QCA8ymN~~2*LY|wI2O+}9(s~F$2r$L=t=NNJl8zv1F-g7^AMc1`GxCQXeRh9I0>2o&cHKHLU2xF&VHcHnVk8Y`WX5*^d9(c@NH;1bFP(~FGEwAb8Y3!*IuqgU>=+c;5}i^wVQJxbM~h~1m|Z6&d;H@z|X-qp*O%c!B?Sn@Kx|R=p*nsa2E7DI179YdL4WXe2O{y)+q#M8>4xNYXbB*bIx6yFF@nKeD2!FXx`$w1^gRWo9niqKCWBAHt;FveqBEMkuTRny8I8}{<!Ye-S2L+2iMKI_SuZ~<7(BlrxoqZb*HZVcjEaxgYJUv1n&ZC`xeeWK&{{(!0Vx#!Rx`B)bRBwR=i4y|MXv$ogYOU80r55v;0ltv7r8&SJk>4hlIX9CHWZ@E3W?Io9q4jM27tvi?GKB'

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
