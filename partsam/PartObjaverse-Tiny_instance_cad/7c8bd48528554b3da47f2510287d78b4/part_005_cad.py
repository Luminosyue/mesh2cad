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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/7c8bd48528554b3da47f2510287d78b4/part_005.stl', 'relative_path': '7c8bd48528554b3da47f2510287d78b4/part_005.stl', 'source_sha256': '7266940bb652acae1f2170b0de30f96e2ba9801d18ef11f6b53453cb918d9669', 'input_faces': 248, 'input_vertices': 190, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.04160767048597336, 0.15647615492343903, -0.03769413381814957], [0.04003683477640152, 0.19286639988422394, 0.04065193235874176]]}
GEOMETRY_BASE85 = 'c$}q~4OCTC7RN6lAcTsDl!|u66hw><Q4z6s6*U1hL@+hU2MB_QAfSSxUd0p?`Sc6<x}bojjwp$i8n-bu%hl+Z)yk|}uEvb~SXtIIqciXB{eN|xHM7>NnYY$i|KIz+!@1|~v(LWgJ)$CQySfSd8YDd9^Z4^9S3%I5v*0GINXp7dO-#yueraZ&jo?DQ{<3Q2jM(W>b8Unb!fLODN!f{6ULm4aXmYTZujrMWk(HAbzjQ%H*1{y+pAx?$JIUf_r^II_S>AgGjP>^wM-KB9*NFe)%gHhYwQ71(hehT3W9Lo!`<!D-bXDL>H{U*|zt?WtnspWKk79pZZ|W}%{#qujb>FA^LYIG#ubs3j&{c%5jvhhdNR#g5(fC0#_mV&K68U2IfJ&n;tMAh|X1@WIbiJzs$k#G|ewX~BcgND-!I$o=xj_Dn^eobf$VS~4Pn@E0gq5{4z64+EyiMaMojb~mzG`=!?{{x4U01aBzkG<sm!H{LM)RA~zk%*Iw3f!v&W>4TGWh1lb<|(+t=~ZNsp_uKIARHnFT9doWAvr--FW^J(rfhh%J5<Jq^1Cl+vd)4x-NX-n?%0u!>dImgD-X&`5s;O?A0O~7rxw*MB{5pXE|NxCmZ&+HPAR>W!t0<qi_0*`l~iyP&~yei|Tk@N2tFPno?!-)rT_0S-Fr=WAvr+TQrW4no>pchA*7&!|VHF2HmgRRK17Bci%zd3zt)pOa@<)PVqPyhu4ws@ePe9T@T>-B&KgS`f_+8=heNX{2sniJCfI>TSk?!zu=riaZ|(7w^JO7LwA!urW=hTn}fH}_2A2!Quw+qr)hnyzG8l!#u09u+Cb|8Uu-Smcvc2)qjfN6?xK7cbe+dZj|ivt8zb0{8%zDA!p|w6#8o|a(!Aaa<9#~*&=bD=V>ItauR{%VefUacADWMt>rHv4%ot4fCk^uBJhac*ZuEu7Sn4kqrj^jR@Xa+7c;B5)D=`^-@%$oQ7cqz8FRZsAUu$`q##aji<7r+#7b|GIWm|Y%9HS`DtiHC~nfI4xRK2mk5LC?Tk~o9%z`Q1y`+Gd(JlXYjK8*)o4P46iwW;+r>L2D!zIjL)@1uN=UtiGsUG=B^BzEl}Us>RsPjP^+4PD0mo)cV8+}dd03)MgK{Nr9-MB|lnoXpov6o0w>_&ORFzFf`q#N0)uc?yfClCORFDX+Vo*JjFxRQ8pOt=!*~%YWam3;VZY_`cMS*VE_l%@cTh#dG~8>i=jg<*Dd7n8ueAE>hjI`bzb5&gU%-RmT3(xooZ*Q!i58Gs9OS!#NN4Iq-h3nL>3%^FPbib=&b8&A*y`Vagod*LVFk)A$1-3rQ=uE(s4)sGgePt3L&C|EBNv(!8e0n>ioGa~zI-RY(e7JpKc(qgye}PxkwT*ZKZCoDUP6I6vWw3mW-;&m5*a5dYe`k>c=96X$u&b6k($i{Jjhb!<c>?IY=KEbU`0A&vcrJH^z`>i2Ht@iU{h()I85k?HfWo-`lT@7zwKFRzN{=gZ5sRQIgDux~TXM{++$`&PTdzP4l(*Q;f=R9DsP=C!n5CvAB?zs#b1Rp2XGzC3=(BdRmX3cp;s?$o0k&+osZ{VBs29NIW;FHNN9f-or{hvNC!O0F}X#8TdCVeHE_dwHB|E~S(YEhAH?zk7Fn?mL|3{n^aE;x?G$^KmjgXT{D3u{8fQ6W?#sG<tpu@HLNNypLio@1y<!`=e=`Pmgf_-2MFggD+h9mizaQZKV4R?>3#{pX$K*FFe>~^wo+HoX-;jYUy+MN=z!x(>tKH!{AG6OL<@X<p-+E(z|CTQ~!R4xgI_qQeiUqTF?pJ7u6r`ptuYfGm)-)q>lae$rJ~xFI>py`48?*>nN1?#?j}tp4|V-QtEH@Wv?F8U+nb_*Sj^f8T5H`1NT4ELhGWzS1;%Bx<oe6I;w&9sGcd!t(>1twY2V5U)$ftbtY^I&0p#3Pv<qYW+D3@uBN<I;cKEZ=TGx^inG<1BLew(cWZTx(KnypLh&>gkEeJlH@#O;{N@hh_<z(%``7BLSL`_t`+vZBp6^HJP2u7J&WAM}eExv1Xm>e2bsFto(Z@`_7;%W}_Up@wjlS%g!OzW&E?jRn+R(XG8}HBiEBZysLj}GR5zO=7dzS0i{5tZ5ubcUKH}n;%pE7)N`WcQ-?<86mp~r5jmqJl6@1yYfTWCJ;wFZ8^s0Zy!DIWrl(epw2><sVgOh0-r!Z+8%@%l!*PxVy!V?P>CYMjOK47^8mUWG4Q%Hw>#-^$NvYybWOIG>%4(sSJEYm>rwzf8Nw_5aHRil31CXWm~qz3KcZ!IwTM=lc9|Amy9%X&L#-mKmHsMJmSyzNCD`_tm+Wp9jUWsBTGpuW|o`AX+C4z8p7&^I_bd)>HpJnY2HY1^4;7gB&tV248%7IPb4(q1kl5@YN=+=h~pqY|>HhkT0j5=R8R^aa|tGzSP0>L2&R{N&43dJbpk0ujBntI$v3Rp}i}|?NO*g{opGPD*3rHF1MQIZ+nw`?bc)7zm<Ws&xH^t+Lu~8*HtmBU@VQFSx&wbbC<urG#uys0AKjqa?YRY_7qR)yd%{o`P&wb^Nra{C~x7LCl>O3?VmS`^sGj{+HWj>FSwRp_JrR!hU5I`EvgSz-+U>K@9R`Pt-EOTCoSMQ;C^Zc&G+xEbRH3Y?ZMX_Q=ew^&9SlUyJXRMOgP#`zIY>?_vy`fROdzb!oh)jz76_>;~%n^@>d!h$nlI0iKBIYV?I9zYF#-#KMgN4`qBm7*Fws5IyVT%;ft^GIj#CS?_2m<_(uM|*3*~sWAfzPysw6G+`9JKY4oKaK9_2xuC(q}Uu^T{bMFDyYGZ%xVFt(ZI~P9pyZi5<{yU5Kd*9s}`o3xP6|Y;I4;LZ|jQ!P)BmBMZ*N6gRe`#iSu49EY%V<8Eyy*J!ypudm%!7qSU)=Zw&-2a43+a87Om$rzn8W+AD6Wpig|DXm$k+9mP4_EaaOBU+XLEdtKjM83U!66F$M5XqJb<rMzQA?tN++L7;R~}RuK#mB;`3|Qk7=JttGaRAMtiKH{_utL5{_Gq2R&D;zIMW%^DVj8W@CTZuZ;I^RWGWu>dhSfURClw*YleK#YclLM_uCkebJfXBY)mVzV_51KHr}Ene!jMIsY`D>yq#Db9}%#KL0k~;du58rE~9Z{#UCw-=as*xl=m6j-N}WAinO_$#YCmPy8B{_CfXt(b*DeOLG+5gyeX`Pf@z5zpVQ2e~L;C`mcV93JePVe}9TvVwuA>OIr)w2VM)_1w9Jh1+Ir42iJr5Lr;MBgAYRA03QUmK#zc1zzxv7U|n~D8^9H4I&Xl=;0@qBXgW9#ycqf_criEuIs=>lj)lGejs;JJ`hur|Lo6*2>IwA)dxBk|1Hi6eC+O2)C$Jr~C)f_`2z>_Z2zEo$`B|tp_*t+&bTZf<90`2|90`ttt^mh@v!ONMY;XzmFt`NV1bq|S1a5_%0=I(Op=ZGD;FHkP;FI7s=v&}6@G<Bgz{kMN&{}XaxD>h)Tnf&D&I4zG=R+rf=Yu1l!@v>X08100eWAm^eZel!p<owqKd2YDA9x_t4?Ga;12uttz~j(#4u`%34hP3T&EObtB6JBj5u65H3r+*)LU)04!3EHIZ~?dyx*uE#u7(~2SA*-IE#N{++hJ+NXgcqK)`9ELe-E?)tZM~$4_F^#6LcfA0<7x>a6WVubOTt|Ja7&)6PgFsbul;vnhaeG)-?gV5IPr{0M<1YJQw^jn$EMJQ^C`rQ=n79x`u!!LPMb;U~9b#MbmjKn$DvwZ45LBP3PyKf#4y~{?I_MuAbmN(C$!Au&%CP2WVHQD_B=2unn{e)CsJs9aw<cLhZo1I)b}Fdq5q*y1Iegp&n2-um|`#=(FJGz$2jk;1S>n&`9tE@JwhNcqVuOG#k7CycAjjUJ70hZ33?cS3z6BRp3TwJGc>i0D2O90DK7A20jFS9eND>I#_`=gB9>@XeoF%cpWqgybhcJoe$0c$3r8)@!%+E05}RP3BT8F2~FqWmNppL8!Cc(gPoy$!OmcNs0-L0{1mhw_$hEN=s<8U@F1uUco29bbR0O?(neX@c<4y*Nc7P;4EiE;99Y+I@HA*NG#spJ3^*D*8%^gq&_r+&bP+TWtZN!L6}k+X2G%tfybQb?P3P6n0`MB>YtRC)u9e`;(5=u)u&&kMBItH#HCWd=@OE%HbO*Q`Tm~%!mw~rfT2!P>7dPAg^snyUU$S1zp7_W2zy9TuUrUUCSz;OMw=XGCk#>6CS&Cg33gm4)lZ1Z)s};cu'

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
