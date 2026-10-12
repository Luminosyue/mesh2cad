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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f70f112151514494ac859a50fa5273ff/part_004.stl', 'relative_path': 'f70f112151514494ac859a50fa5273ff/part_004.stl', 'source_sha256': '74058ff8b1f512008b8418c5bdd3d1fd6c6b337eb2fa73659f5e02f98c3f4b4e', 'input_faces': 160, 'input_vertices': 110, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.33209508657455444, 0.31346824765205383, -0.07037782669067383], [0.43905943632125854, 0.42825576663017273, 0.06803121417760849]]}
GEOMETRY_BASE85 = 'c$}q}2~d^S8HRrl6hU!CF`{0r3J9{eAj)=8BLcE2C`jO5^b!;micvxn%}qOvRue~q5*LzOWD%FTMFndduT85-swR$6;}Ublk<{3fF-_G_m;UE_Un6$fnNG{hnfJLbAK&@Tcg{Wkuc?V0TzYHx8LavHU;6QLcTH2Hi`H9PYAJnb-W<!~phYF+PFi>I)z1^HNX|$~&2rL~YOnatwJe@f>N~;U8(9$U8))z?C@y`e)VwIKxOA>X`BTgb7F%?GaiO`yqJQ=a4Gjr2jP?&SEHnI%KdK75N9_3+T^&AiuP8O1%&j`6{Mc#mR~3qHZP>S2e*fB9@eSsR%SvtcKS@;a#&xyg+jcl3Pg-D-<oR}w_|_H05^vZW^N#plP2y`;4_|H{Z~PX%-LM$(kIFX4=f|HTzEu<7@xjb#D&9KbqWGq^O7X41A;>@8A-=I>Gva5aOCIBq7UVhf=Sx!WSB~`(U;iEQjEocC*ymTWF6;0Aiujwi#karFvqI*HX+xb=<Hgs?-*{W%lbtTe@6D0OU-ZYd^7|l9@wE%BU$*a?eO4dwZ3Dg$-#%#QI_bk@ALQ9`OMJ)B6Kmvi@+k3*<64pbmBV!spEMc%)xV2x9r0nU<lCK$dA;sP9z%0*wbWUZj(Mm5TH*~K6xS$UGfo%Z-YZS|W_q}@Ui|m6;2-ryKQn4%Ui<bO<R5bv_18q%L^tJ%ZyLS}^VS`FU*^rsN1bu2F>ik9R*7%5V7-rLVjuIX>%`9}!o2x|a2~$jEbB6s!#7;nEBQ@%=iZgSbFW4o1NPHU)d}lL{{-{?;p;CX--7j0k5<#|qWDX^u`es9%DS|Q9^z{r@$e@awu$dHP<&I}I_&#Ym;KU*^daIq!np3b!20&S@!UY<ITkAQYkwIgzU^)bd=J-psoOFV@h%V0H{aaf%Dhb>;#-$ZllqNE&s2)vFbefFHz7|;*bbT3DO!B{`YNf@w0!<P`MaVxtjpno`UiyUlDyUF$nO%0^FHaiP4fIL1Mz`=IRA|kq#pam9Ptfbb(4Awr(a$v{{CXj+bI<L`<jOQ;pgB#=!tojyt-4)?V<DN+rjrFk148PqvW}EAAM+BhWq2}ZrMls<VWzg#-e|I(b$(;U1j~+_h!_yF>;mohkL<aGZph3zbEHPyWbmrQx@v#oVZ=$zr;B(p3IUww#Mo-Ik!21;#)(_h;M$dO+FvXfPeFS^y9+8U6Lno0rLE#5&qo%d&Qq#g7{xFpq|?Fol-~7Rfu1C9Pvj!-7Wr^O8CoKu<lc?$n$U$>JLASI<w2=-qxzO;~f0hhCXL}hWLdCaF4XKBF_sI$baHv)N|Se-=mw|_R9K_9Ejg{2mN;|Y>@r><_6AX`f~KytA362$8;Nc;&6YMR@KzXe%1c~|9A<`ZO4cVi9h}bb>`w;aeNqDBlRrogZsA<_mg&H3GSb=0QeDzH{HF5d%(67=dy4S?z0dp_OW;k;+vP?o;ccq{pz#@_v8GHxW6ymc~{nz)&PIQY{chQVIRMS?>JC}=b_7|@*K4H*o%0F8}gKIlY7-3@Db{{F$eWrythL>cRY{#I&(GF+qe|@%@+~B`j_bQ%s71SZr#MZEeW{CPDQPi_$@7%*SG@pOqqsz&*wYD4@kmu?Blz?k^WuBbHZL*f&1^&M^cZ`?FaY`M$|trJ6rlNxgVa#t1EG?mOEF-yc>eVw}<#5|1cY#Q;*?W4Jp{K=(qNXUpp3gdM*3nnfw`HxW`xfqyEn2Z%SNYEaIQ@Mm>J%vn9TF>gD$5L_513=d*4Go<of<BhR+7t#YnDvmnotd!w{bo=4hA8~nFo@Sf7TPtK>&<$(Cw>(3*8d^4U$*Ulh*N(t7xdo$vFnh`%?De{yZk$7WO8~U@{1b@R8JRi?`;(h3F0rI@KU(UJJHe7t$<DKZwm3X<&?eByj-eV8^L*;MF=j>#>hq<r7zLee0m3o?Hh;QhB4d2J1;gZL?Cl`Lgb@8nary@_ltH{%K82;-w@+6P_Am;tuCVWq`5=^r15nZoJ9c80X&!0wbkviY(C%!f-4E3CNSQ(T0%-e8NTFz<BO-Frn*58H;%<W!<<rkXvlm7cx;dx{JyI0|`|NB*Vpk70OJ_b>J$!a<MWI0d+c`$jbKBnm-T_4k_+2rZu4C-uh204v7lbl9Qpr(=&$djm3$dkyUsAI`vS=%Vqqw0&JK2MG#kE4zuk0TGG4kZsGd$SL!FWsqK$=%7_s2=2Q<Q`N{au4zVsyEr2b19BgM@%2l`WR15q|PEIlJhte&mk+dP#2Ib<QF*<7m<|~P#2O5$R-ZObM=u=okv|ro=2WfEh5h+7g86H3(02c9I~05LY+mP#lEC)jY;f*(%5!AiDl1}29s4x6g_q3f2KV>?;-ja$)R|(J|^oUOdk`eqsbG=QPdD}6giX{Kn~zsq10e<Flz~=Mv>KCWO1*QX13eAOs+eV>&auxWO`BbCsH%XnT%1~S0C!%zg`;7u+pwncXC&<2elK~gX~G|LiQwkb0~gJA3oI1)Gp-CWLIh@vMbq*>P~iN-HO$n8?TQE8oski<EZi4)9<+AbPmP28qTfK8Ps@kJo73J)Q6uw!Z{R=<xo7BeH+Z44W{qK;m2D2n5!>!2w7<#a$m9=RU<!nM7UBrwChg?_D`u(yM8*c-%9(FeaJyne{v8xhH50okY`YH$TP_K9E#QV-b78N=8%)g5mX~Nf;@uiPaZ+;MeR@SMeay-B6lP^Q#+8I$u3ll>_YBI?L+QK9!?!X9!?(5p*WfvNRB2)Qp3qgr;;PdDbyFpDP(oer6xK#_wMkY{wwY2k5w)7ng3Y(*S~!BwWIxCdg@=?pI$;z6J1sR^kzA0Ki4&0by@o-H249N'

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
