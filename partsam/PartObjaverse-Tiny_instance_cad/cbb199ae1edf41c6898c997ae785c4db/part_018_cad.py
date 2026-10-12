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

PART_NAME = 'part_018'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/cbb199ae1edf41c6898c997ae785c4db/part_018.stl', 'relative_path': 'cbb199ae1edf41c6898c997ae785c4db/part_018.stl', 'source_sha256': '336b7600caf1fd44bc3dc9379f8504333b3b046fa4b9bceb0fd79893f88c16ff', 'input_faces': 191, 'input_vertices': 239, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.49999991059303284, -0.2987701892852783, -0.195845827460289], [0.17709165811538696, 0.08872975409030914, 0.19582825899124146]]}
GEOMETRY_BASE85 = 'c$}r0e{dDm6~`Bl5Cv+mL5e}xKui2V`E3i7Hm?{!ifF)u0utRw0!9#M5`Gn}OQi}z5`>TvQF$UFQmud`Kq<UUNCHT#R4R!4daWc-s<hKTN;^}a=k9*bdiT8TOs9P_XTIO}+4Ii5d-v|WcQVNy+vbK;!~3Kg$rYn#T)fpVRCF*>jroPerA5;UOZv{9yQr0s;&Sz2UGqThxa`TTjQPgmjDo_FX~h}C%#7jFhh+3IGp5feE-lWV{pg(Hf<nbd<<BZ9Bwq4({@g<Pe#gK;L;IM6?(AbeZT^p+o2U!X>(|f4NbL?ijwy}Dy4PiD-1=bmM`7G7pAg{o1dltYV-GpsUgumtGA})lZ=-(n%4dOmZdc|<&~CIQn9u#;{OH^>9<T7YRrJ=5SO|9-uf6N?lI_89s9JX*Q{(<P2=0#qxcQfXq3ue}?M7PCU2b&r+I2SUsn@wbZXNd2XKLIZAHn@`0Jlr)&j#vPU2Apj*Ad*W1MaMyAE;xluB_8J=QB696rR=Z%gW1bh=p+Dh1^=5bA9LUIklM~JbpN*LFW$oFY7ax_4$5fegFB2`Zn%M)@Ls3^Ek-*{yahb`15&zafn|{a_cbX`?VU{)#~|N$LFU<2lI;>9G(05;O53%X9DASwz*d4em}vZV_rKGn4fz$y8UF%b&O|U59D(l=H}^~Q|^4KJ+aOGp1o{$Oykiyj~lI;>h*l%YE6whzeRrJn#Vccnw@+yte?zfKbgyZ#ykJ*6TMEfOSAV}z~#6xm*ZwHdn{1L*jVqxG%lYP^MvQs|NcN7o+r%ZJYg>9iM1~)P>1I;bNPNTm+u#I`Mxlh^V~=YZ&z~vJxU4o$A6Df!u!cQVI2@$)=yXmQo`@cZ&$7Zg3I~|>p)8Q_(VS(6u2*5Kba@2t8ZUF;r`z7-j_&Kle=Fqckq50lauoGeCJ<yk3_zW_sh!l@|_;rPw4%z7vJvaocrVRS=C<sqEe41_pFO)+y;-&xH~_LM^~d=a0{IGaX<gc_@i#Vs2>53JQ=L-^Ri%l6Wm07^O<EQ^m)kpFLSy7GUs_E^X0zGT<*(Ga;{fLoR^r(^AdA;{$Vc9Kk;ih9&agWa`lk{x1Y@8%^tVfzQ0Z9QE)Tk$Tq!>1s=a#P_J|2V)9=1x~Oko@VJo_tZ#tZy@U1b7LP|!KXT0D&bW?^?(Y_kaMkDQ=k9U)32tTm<GB7Dt-GoZ=v<!bnEUI7$d~6m=JLE3t(+IAZ=UK|t8=a+x&K~+J5^KGx;m-Oou5{x9yKwI+u+8f3**DMHGA3k%rHL4tkJpkM!&#(U>*UtMY{&`E5UY|$E{$y&L)pXM7vRNo<Gdvr{3GC&mX@&xZUgG_%I$H9Beo8smFQ#7)|Jpm_I%j^C$lBmhCQYS#!i~Z)cvPa|1k{p68vfz|D$(9uCX5%015c_7@X(y7k36$y~0JlJh#rT&|OTzE~%j%XKn=mj&y~b<*!Y#=&0e?IQ`iuF284#p78LY}e<{1>5Cuj`nSG!nlL;p5IT5zwD3CMSmPT7iV6uKR#b7#u;4phq>RM%8C2jc1Kou=Yb`rJFl1<;L-NW9i2N_$UnB+(d$IPt^3j&-MTlI@7L>FSJxekX`J)p_0<R6@2d=No{Dn<b9oMDF3%6l<@wyt7v~D*^4!i`o;Updi1U2>sTq!bzwzQdhhiG%`;DI4eaQVjrqR*I*|~JyJ*P4E$9YGycV2BssSVU$)X9CGlH02b8+Fd@I+Le2W`=OPCFQW&kEHZky+2lZns;sl=l;Ymrg`T;t7o9y$fhK3-hun=&TQw_k1v@S$hW3q9Rv5rr`Nr1KO^1u2k-ZlHQs&-&iRqTN^iamJ{im}t8nv~bH16o${UA*=D__LM;qMvz?|>b9^T-s&#Thv!t$BR{D_lL7uFx<vOmW05p`kr%Us^C-K8>+&*RBlj%Reu*+9PkyujsiXP)rf!4sbEvCF~!V}44`^OL!ppOW+ZbhZvV5ca+>m+y<Yp!z`A`^a3rkM{0M9>=<EJh5_DOyefFHDbjsJ>S5(E%R-xw|@TTIA4qPkhxqB&8@i&dOoku%;oybT&~Z|<@)SwcD#H(C#2rv)?v>3m$_uHqv!KJCG&ZI;e7kATO0NI{=NpDu+K`)`z(0EJ`0|(Z*seG-;{i5uzq0Q%ntmO{GH_!(n@bM3>7yTsmAnt?N8(ist;@UpU8^_|5tw^A24*l|NAHMuGEJ<6e-Yez^i-wzPeB7WAG}5<GRv8@D_4Pp!48W48?V&--2I2@need&>zAt!uR>m1@Mnk%%Dhywu5g)(VC(&^j7$<!FPnVhW{$X-SA59g#S84UtCw30bfAzJ&Jpw_rR-ueFxW-4uM~&o-M^hXg2&p+*>JhK71j?bc#068{m~D!7FVGZ{VI&p`GDXbis9{?ctSnfbW3cs81(~TX6jrTvProT)P9>9=;oe31;Fq%6}8rdP6(G=Tl6hh(Jfce;3yVLnH8|7?XVHH27h-_HAfB{5XpHDSATF;k!d`ho-~dhrBV+aqtxsFH%f`PJv%bv4-Li=v4SA&`Hp#@D<2=5xN$>E85S}`jLegiR(&lgTD>;&=q<+d=`E?5;_L{L5c?qZ~iLn1#d!oKzqUe0C{7f55iYbR8l+&&4Yg!IvJV=zY2M)p;hpsQLh`+gdc@#Y0z%)Jg?HAJ>W;7ucM)3;oqY81;qsDL-6lXyhD)-&4GUiIsuvk-;ZJd#a8Gq;Z?ki>q`5>Z$r*N=m7Zs(0<SX@aHJbQ2Z8p7(R|`o1m}5@1cm{yV5t|Kc?7D(ExoD{vgF(iha=S@JA?4P}D*{fIonKyazo2f0p8p6z@Yn)chYPHbdWlcPM^Mu?4yreh0;Ic%_Z-zo9sU>q_^-e?rkjaTHnyuliGu>q>tG{}ILSC~BZP;eStYjAA!*7yL<zQxq$pW$>Tj+RvdY;8jjD@|3=!{iX~#W#GzRp!gHTI_OLAUr_v+A_{#K{w3%-=&SH6Dat86g`S32aUR!|z6{@joQ=?O_?Mw8q2=%wDK1e|L)XJ!rudxVHRuNT_0VeQ2Kc8beoC<zYQq;%JW25cbT+)od7k1K=+EGPLh&rcQ_v;wGb!d!%!1B^UrMnIc}kyy{|d#;hB{z*dJ}vx#S0Y65z7AvS`42(wpHuYHvj408ovD4?q;d~lY{(a@TjN%vNvtQ{=qMMY+JR5(;=j_+kuZw_3ht<wE_Y'

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
