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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/423121778c4b4e849a029b8281c68bda/part_005.stl', 'relative_path': '423121778c4b4e849a029b8281c68bda/part_005.stl', 'source_sha256': 'ca2ae086be20c00a81fe1fe4c3b059826dd8de536153a21a142d854a1c7e42d9', 'input_faces': 146, 'input_vertices': 166, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-19.856313705444336, 108.45843505859375, -20.863149642944336], [19.8560848236084, 161.73619079589844, 14.557371139526367]]}
GEOMETRY_BASE85 = 'c$}qJ3shEB7CyX!5Cjo~Q1S8-6c7Xz&DS-{M1;^nLliIZFc4p$1PXf9@_`Z>n(zFTv3!))n59|M?;{m02h$Qm^UuacEwR=p+L$)ye0x*mnptbs46MEO-rwDKpMCZ|cb{|qltc$dZ$W>7;-NF8KYDr!p~y{mi{hNZ>3LZ>McpP(EwvM#z|~(fuTD-)N=dU5#bQ=ic1}@NVc4TuSijufVUb!`?v%pmg_)DbPbtjKQTUL|f}$LW7d@XjHAm{<-Fx+l)Z)5CYUSGh_~$A^Fyb5HtdiRT<Db)&zRurE>6VB!z^&sdGZn5MXwYCcWj1hqVl3>f$MS#tSn>37@-yBaxb8Y82=9NCNA{~0!jCaJ#~XHTL&<-}8Q_*>1Me$8HvfOdD%?Ex9{iZ;9Xyq8OgaW!q)vprwlxIy){EN-PuoTDN7OY9RPR;K0B&sz0xn8+-BY;cQwZE}_a{Fu{_LT2tuz<7CFXVVQ`v{&e=(Z;&p2SfzBuO!;tX*kKc~NfAE7&a3;(T}y5qf)mtk*t-_s8Mdz=PtMsFnhWB20VXZ~T}V&4wn=Cv!4cz^SL;Ck&{@-wK$7w@0kL-wu-6pv%&eKoG-^>x6tkjH6W&i3CZ|N7olH16Mm$v)xTdWD-W<q=+Z6}W9t-BH-jGYJ3Cj_N)&IRN#tPbB<WIr&*0>Wq0jVMp`r{~>VEZ)98KCG}Pe^11l0;}O5st5L;iZFK^;`T2g>n_;P_mtM9OxOjy8TRUaAL%*?v@BtUO?nkdGd(k)txPE*S#kq0!K^4E|HUqeICDmQKxyS`^d1VrQFPre}w~=T4R2s#TP5yPaklTo7-zebP!I6Y}{O~R6HRoxv54?kUnK`u{@ONl1*&p9Vb&QF;qWsu?2?1`q7>Icp6G9!3p8~@5w|Y~3v!{81zu`^uwJ)GJKXC9teJTmJ1ZKd$&3)%)_%E}gcw#Cj&#pUfDcp$qdo=uS&Y^m3xX=c1X%~Qtiw&?hPJVq0bw6MQZZz4G|D5DEkk3a7fm?g*AwRR%`r!TNQ-PaXYpISW+;5^TM@Is;B&>peYwM%Olpo9PTT!sT{x;2Pr>{Tq>hdXYBQlEWK42#DV0GRHT+FT|`!9lhf#)p+t_RPe`EEardWjJ)k^k&0%BNE-<|_h|$$y(hs#n3`));r)VBogp*Wq6r`n4<SXWYQL5K9)oUJptA2>vZ|X}z4R1Fmgf_Y?A#{TO|(ac6;x;&JF3=CGc?ZG%E6KRzQJ;s47};O6~lG~as-Ziw&7)(G(LjvyXAIkF?(TmBB>(rdkG+`a9?;OEW|;MNz;jD_97IW+%XwOtVZsm?U7zfix^`rE=$mztt+824Hubo13M;MROc@_();_4)AcI^(@*R`{{FZ>4p1+y%H^lL9~5zWX%)I^PiZpJ`?&+^}m$>%Ouo7(A_a7RGg%)D81Y{5%lvMeGNzT`i;WzIeD3{7;)pcwqqYVtccsBk*7AFs`vMhy3RywMSf^)li%@A7H+^&Cd^f<t2)9NdWcDt@-WnUQ-bK+otZK?`p((>`RtG1Id5SeEOb8U&4N9?b`@@%Y?b17|*B&ZalLn9rhaokayGhU>n%?se-*;nMmvA{jt=~LffETwi~VC$9i)y>MurjBtQSKbtC<-3;gF!0B-)cg6evG)-P(^87H0uZoBM5_IZo%qOS+-K>XsfB%1H1Cx6C1Sx^Fdk?o0fBfQ(+hW&zTz%9n3$iEOn`=HMS-KBa3MTZg|6OZ-2W;NkYY^3i*TnR-VdO1EDc|JSBpYZ7^*oQ40sE*Hdp?E}xRP0wyOHnUt(oCEK%%o57z3R_$-s&lD){@KU2O^#Ge}wXHOL)&4^Y;qHxFX@tH138;?SMN4!`>K6^%Y<H`C+^jmw5fqdN4M1ZjbS@Do_{Q-a_B+uBU(-bv207Qbp@Zyj6nl^1*c|R%Hgj{}BOu<M#O;3fGsk?WA;bDXnMAyiQop7S|6o#O*PazTfXgQ9s(<09+rmp7LCFJQB|<ZUHxg{V=Y%Bo5z?7!V%_yWNK=Zxu<f*Hi0(>#p>DSx%LAMm(zt7dy^SUCuoo0XyLm1ix)>A|CNs9@dpU|4G9Az99RmvM$iqHw96C>S_HPk49fIzMK$@=gVkZ>!@LfM;l%ZT-(HbU>Em+b9H3@%Y4GecZ>pWbO=Elo4&_<EyY97m$Wm!z)kKm=3O7;-zYl-+}ILF`JC=R`%`IADD;9YG_R;w+W!tL1g@><4qQ7w9Q{k&t_7|y*g^9>JFF}G%DxBufxc(NUM4(&`lNQ~4T`5?Rv6}CUr+1GKN5XV^V$nscMGIGx$S$@QI~xf_7C>qem3AH_igb#^=;eMTGT<*QlB@=xzD$^N4%C=%7gyqPFh#DhX8+YztDV>Dc{ZequnRiAGL9#fSYZq3C~>bgz<i@2d>ZCP4m5%hJD<YmfH<>QFjPW9ohkSbxbtgJC%rhil!*q$G43HZVu&h!u_Q<Cz$(c2)|&Vaf_GYoN3)_1+F)rPcHYz`9uU>Ap7%to-xnjJR=&e)3_r(qIlAM5T_V#7X$m|^U}$8ab6OW+XA;VpSy-R)46N0H`)Jo?%I!Ymp(iMxZv}fwxAGw%9a=k-1wT$d)oqW-ZS%`CcOFFIQayf8|66@ejYq$R;{IY{P;ZFY8>_tebj3dkMCo&K69?$Ks-Mj2d*`rt8b*?Tx|@v1zc}Fhfg1jbGS&d>yCK)(Yf6`Jp$);^QU;=*1n~bhxY<04-LbBn^*b#zcCzju}m04_Q|KoK6ecIvYDR;T%X4Gi`6^ne)0Ay^7Ad<NBXSBeZ;b75BYK7dyQU=dyT$*KiMCldyv*)GwwkamnPuG3w+NS?T&kvwKO^w`7Gl5+NIIBujwI$gg4*&K5oLjPh=khZa%~J%9{bWSBhho2={)6=Joo@Z;-bWd2zs3@_lw$7S0X&vU1>BCf|SirePn^2d*KU@6p!NU*Wqp!W)3=o%r5;$Ir`}@`qm&`t83n<5_1R6g@1wMQ&z`pAr<P{+ju}|0yA_$A9-zLXZFZr-VPr7-}SKX1;~xMUq~Yv{upz)|Fhr`U2)vELX9<j`>=a6>X688p~^0w=lMm`39C(NvdSqO7^>s$5(z|VqU@WTpr(S5r>jjN?Ol8*Yli|93rWYq^`{4S$>rD5SA5h&*Ud5lI2K#9xN$LQb*>2ENlF%1M`k7hq3M<sV(as%#|L&+=t}|mZO;av#eri!*M9yu7&K#y5e>$tKW*88B^SeWk;3;b9?dop94R4U_Xxh+(ptuY-7)|1M97rKg6;#kL||1HOp=+dolNBIY?3{%ZmH5tZLIu(j&~nSq^7CmU%ChJvh(q%r%zXS$>##0L!5~b`0|#EO+5&am-^_?#1K9Gw;f>BiF!{xgX1=lBP+TAZZ5c&9dT#q)DtRIYUyWq%o4xSXXj7%L*IKdKz=3k7YiJ<*_V}WBx45k4qXRX(-Ez4`NK|Ls(WknfdS*@)NAL<y!hM_iZ72wWyyr*UO8!%CR%Q@4>Pg>rSkDu<X&IcB)qPEZg(*=OyJzn#_DE%Zdsl<+EJO`iqk0OIpo*G0TcJNqU9lSJ-x<r0J4!m>0E>UywA1<%z5(Ng5&PDdwpy<dKq|VL65MY_3xt%jvAAv!20x3d<QRXEHBgIg{mbmKDzu^c{8*^o=U+*+Nz|AHZ@?)|W_nRnk1pxB5mp^BiaM{GXFFUQ(f;eyG;CTI<o0x=ZRSX{MxEg4TT*=Sk(KpHTM|A$m)COj3VIYHwaDX_=&jg8Kg&N!5b-^>RVIT=iGgE1UbGT3@Os4wjT4=}G2KOG;EZPPDW4cKA;}@&Ep3ss{ImAN(JD^N-tk%QusyuirNJltd@=Mtk|MCjO0zQ2YyON%D*'

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
