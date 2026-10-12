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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/404f12ba60f444bca620c4405ef50bab/part_000.stl', 'relative_path': '404f12ba60f444bca620c4405ef50bab/part_000.stl', 'source_sha256': '5a628b83ab821b0da9fd16bf1b035461dbbf382c227a7ce5f225daf3643923ed', 'input_faces': 276, 'input_vertices': 202, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.39261674880981445, -0.3738255500793457, -0.3576623797416687], [0.4678552746772766, 0.3639988303184509, 0.23846852779388428]]}
GEOMETRY_BASE85 = 'c$}r0Yj9Q76~|9_iO~co;SoV|^T6;3gopAHdoNTi8lZtHNGp&)UeuU`1VexVmx?w<5d<R&Lau<d1uC>46=}%@<zXR62PA6CG|JSOT0YpBcKSg-bnkP1`*7|$hfb%xGi(08^UuC(uf5LRhnq_Z3p#g6vz%9^b?xHak(%C?rQ=pB&8jc0UAlNtY2Apbn&nAWPutfoqnl?uGQDtal2vc5%q=OcTU47nF_b&0Y<zBBD7UP-c4=*K)q?8Ul2YwIP+VD8s{Fc&;+j%*J$UrU(RraUL-InaLjU6{S=X>L^hvAMq2u4v8oyk9zSZk*I?@={{#REod;LiK;s@HdvY$C0_W1GR1?~DeI`Xk&w!dw`$M*Q?O((R*)~{=8_4x6tgPc5{Zf&#QcWHOKJ$^>paeLgP1Ls;jezbDa8M~hLH_zGHYoO!LNw>#`R*$jA8$Z&m&>nB)x1Y5&^~=l7&s*a5`?loU<BcEtWcb_mb>XZFUf(*?P;I}jBIT0TkB_c#>d7rm$RC~4VD}}GaqX1Xj~$qL$zJCl|7Q0mKIFjsp#B?Q_RaN0e~j<z1HN3Z@#T8mdc=BNU+f3B9?@raUeO=7PI({Ac(EVc{9?adUvFZc-F4ld&vJjp|FZXTIH*7PzW(6*`eX9Q_2T>LH2FoH(Z60{eBymHzU*^kUzxogxgU%#`y8#!{5Tx2uZ-{O|MJgm-?u-FFZTn!?|$L?o(~JA{z+@cpDUbmcy_kaZ{f$XR-N;XkDKuiSI!UeBk83ZgZ$_hd(L?Mn8{NTI_jM_)Oz)_ou?(-9OTE7{&g@M;73KB7QU?0__9vphn9bIILMC=`Qn|x@!y0`CG_(c`Ng`7@9Q&u{KKZxL3vEyB4*wb*V?`LrEl{4eEQ(aLm#AX`Ye6ZAK!TT;~P(ZeB)WK^l!A@BJQv8<D>R`<lR3$U-ZHC#d?h|=QVyz%o{U#L_a%bPq`FSkL!zij4%6dd|y2#kC@l^Zk-FyT(Rq{KJTonDgF6Yj~~U4to-t@*N>I=X!}oo^f@PwmHFY7z;h~m_nZpfJ*W7-b1HoIoC@DPr^0v7sT^<4DZcNV3g11a!gtT9@ZI}m=9TAE`0jp?<LRewyt(gkyxBj(ch9fz-SaEQoAWEjoAWEjoAWFD8}-3Gzxcj$Dty@o<IDPuFYEW6U;LPSZb)DBIVPVQ!k2wEzU-SjUi2*{pFgI4`8<)n?3;O>$iB(vhVXARuk2gAapuLK{4wLpei~oYX?)*)PG5f^@Lb@>cO=f+(ckf-VqW9R{GqcO+Jf>}_`Z3KUnuItm;LGZJ>z9P_`Y-T`Pb)y`q}Z>*XIKB7+=)s`eMDt_uWT)S&#X==c@-_?q~V=(9JJCA4*?7uZ%Cxk?}j^xi;g)Ig+0<-Tfv$XZn1(Kh1j0b7s!po%>a^#CZ;6{$q8J-;w#x!13;LN%)~rdrt=Dsrl?w;JkNyb=vDkhGsbDIxDdr<I8%CFY7VBtjEnG>T$=5dSbn9cJe>C_DGQ5(Nc3V$Pd*wC*+S-&$<|t$M`Z&$LvYAU-ZqCLqWbJ))mK>{c(NKpZG&NF9h}3`0>Z*Gza;z9^?DwHF@MdIp5&SoBmQ`p#O*Pt3iG|YfZwuMdhV!LH8^2)ThpQ5%n8i_QCjapM>ybe~fR>TbS@|-Ly6DKU$MwSvqdE(yX##?^ksx&M>3FU)3$X>%aS|Zrs@a_p7?&s)paHID!5SJ^{Z+Xg-F%18aR3J_g(O2tA6v3v1mE|3<|T6^GHI@L~8Mx*t9WA3_hnhv2sf&A%cv?<F+vLHEOZ;9sC`!CHR~pH}gjic{$8u>Scn#%OJT-&e6!#RupvSl6&d#Xd9&pH$JJ;taY2{xxgZhwg>fs`$Q&73g%hRK>Sd>_+c~A64;;ikawgc)W@QDn_B(VV(0~@@ky{>zrZoY8?sBW{yI1COnxr?m|bwb5uN{Vix*6c!G+FDn_GY;9sg(r{Ya?B^*=nGZpg*%?r`j;f3%b^fh=9T!QX|OW<;PQbAu{Qn88qsr6NOE4&Nc4sYkZyU=pDocx-%sdz(0Gr9$ChBpwJH>#*t@uZ5!3C%xJu^3%}J_)aY*P=gx*TRkHvv4E49(@j84{t^{!kgij(Jk=H@NV=CcsE>1Xf8vy!Da9~6~!uwEayzLz&p@+@I1!vAT+;%Hp8#LFQOaZ7vUGs=iwLNCiJIp6TA+63SI}VMC;)nqfZc;E75wmo_ncTp8<Uq?nCc~^;yzqssNn^Yh4OgGWH4de$Tv`tI!AFD!3Z`E?f=Qpi|)*cnSI-yacXAAA)P)I<x>Tpk~eAv7G%n#k#(aHS6b$-XCGK3=YF%(RuJ#cmi4kPk<+)#qdOU96BE!2j7D(gzteTp^M;2@V#gWd@me9%i#z-8LfaP!{gBfuzu#wpeHlvmu9^O^fP=Kx)iSB{;eW3FGFkKWpD$!1a5#=qqXpAcnw+yuYseM^KZ)2)bcdmaw1B7QO0Xt!P*w1Q{W$}cud6)(7EtUmi`cBS+}A6J)FX|)^vENioq&+q2KcGom^|}?cosDTGQaJ%sl|T4ITgwLx*^{Ki67wJ)F+9)@*nfKOc$?_HZuOxzuMko9k?9y_2=+b#y_ydAK*%TDyBVjccvRa2I~w6}`#B-MQ{g-wh{ooy<MZ+{4oUMXi3FL;J#az=O~%SdX~{uP@vOO@@=H)$lFMmjb6UZz}mx@o#0GOy(K{=b#}tL{D?LN4ImG4d?LQ9M+M8Z`O4?^Y?&L(R4VSS~Xkrx)a(J?gS4+2fzd25$G^@1e}Ksh4bK^<kzoWXivB&V>IWh7_K4%?FVPTozWz?FZUsf=tD32aE~(45S&jgQ*#Du>V$SiGvE=dAs-zMCsBua^<y1*=y0?jY%xa?+8Hh^Na~c<`9^<Qas3t5gA@MHLcTNc*F5h#-%`2UU-}9Qx^{Dl>101#=jyIl{{~V@t;+'

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
