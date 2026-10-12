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

PART_NAME = 'part_011'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/94f6eb48b8fe44c69dba4ef04cea53b4/part_011.stl', 'relative_path': '94f6eb48b8fe44c69dba4ef04cea53b4/part_011.stl', 'source_sha256': 'bf30d8994cc1da78ac5aee8601639277a9ddcf06c50268224d4a7fd2febec94f', 'input_faces': 184, 'input_vertices': 155, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1169065311551094, -0.13533782958984375, -0.49285605549812317], [0.1180315837264061, 0.14980845153331757, 0.4992673099040985]]}
GEOMETRY_BASE85 = 'c$}q~3s4o;8OIk;BWQdCe4=rqM$l3e9|@v{s~}?FDn6)*ma?dTrV18(@bIx$G#aCA(D)w58z;`hNoYh969ak|t2C+Mp%;yD5O1fCiDR__nQ0nR({sM_U)-~~naQ+w=9~ZT{`~m%+}*PacT7tO>J+Ak*E5Q1Tcpvor=sxcu7oLTvkO))Uy@xIowuquK<P!Ezs%e-E8Us)a)7c{DUDc~UAUwmB2JB%oD&-nrAFlB7pyMG%FE0zSeng!Qr3#XY~~A>Wv$9)?;~R-Oo&p)jf_$^sQ=?Dge^hccki5srQ>?*NuIuWxu1G0-sctGed%Fiyu};v#^v2tC9nRTyf%NoG{=#ALipO~EAf83aye6)qgQL<xS!Ud{|<S@dGi#_y%5%D^+u}jj)o$y)w}21tE71sE2MrM-uHR)RmtDmOkSN|iuL2TeKwMJTs$nz@r4Pm*0oA=+|{p;H!gLN*000sm&>Gn^{>fdJ@ZdU$MuaFD*9`mlja!kzCX>A=4hoYIByrx|2Hvb?VS%OU9JYJcf;$ApLwlbd2o)rWAlEg-$?j?yyBW7dCl}!?#pxTx`l5%BYETRW#lziy1brli^;niZ_0BP#hj*fUWjg#<}4K6s9%WwKa2I;Dm_b|xAbnE)hqD2_dt{6w=N^EZAhrMdVP!V#?@S@Uv&n4MCWJIWvSmt72dcqT<Uj!eg6y{XJe_<?||2?rcu9d?=9hLM|dbp3hS)ixFo#R<dypMhH2GwoRV^>Ux8PfE=v8%!0)Rl*SAXj`T*fIZ#nwE6#d5B8p@_mB(Jsy*2wdPcMN`Hi1ioON&eJB^7{IqdTBnq!@FIYqgS0IuXe0ccn#jZPWS0k=P66CN&Twny+^6vz3$&1()<3Q<b99+d7FD<WwzL7UmWrX-!6GIy+~Y#M{VSl+!K}l?mJ)3aq{-(kLm5tpN@XpbEBi*_S`VN{rO;e`}4ubc}u*vJqJv0e-4=5{v7D=w)?un+wN1-+wW5&=SZc$`_A<C`_A<C`_A<C`_9NYSm|#+nBKl0OmDw0OmDw0+&OzI{q1Md+xN5S?fcpEKiJP&AMyLL^GZYP!`9nY?>kdfE%xDk^4j|a@6zYlGvE(2cg5LykHu@QQNlZq*V4N7k3CLv#%-168~Z}YtIY>7{~mew>!XhOn{Rq^zUJId^Ofz(clo=&+-*^9=lR?WT{^Dmf2`l}pxndXt6y)r?XmWEtf#8p>dp12&Qe;Bx@f_!ct7)XWyG;~%N*Z|b2P{F+CQSi=St0_IeNDq$K(B+AEkRVdHea)p4>=Y$t#oAuME$7*WYnX|M<AG#rnfTPsaP%4{CTn^7j4U3r`?#H1)keefh2ikHtF<M3L8KmR+Ksi&%1+`h91lIZ9+MdG}tYeB3c*ANuW&sUokpzkuiG192T=t3L8~{<TE!Cp2et6#f0?e)N@JZywh%{ULefn=dP^^Ns1@Rdn2n!PKumY7yrl`CsIX*RIvj`_|SLkJaP+X!&IgR&SmkJvrl&)vIr;Bkx|{Rwd2<ejj<qnv~D2URmQ6=l{W&X0ac8o})hFFg*{o@8*in>l`Nh#8u)s`Q0M%dDHHqzg(P$Zx**u|D1^P<dY6ni+#0&_SFx3`vS=;pS>e|+kaZ5{-YJ-jjwh!OTMImymsTo8&<EUHIesSJN$*zza^N~t5tp6DEWmw$g5{ZNM2u>OkR&2Qe*W-oRhqJ>9^;lIf>gu|FokeQvbl6<P}#|k@fuOGv6j}>~4Nf@<UFD{v+?bFZo$DV!r-uwd9A_lK1U6=8?|-ycV&}%p<i@|H!|H^RRf)AEo}69*X|b_ByFQTA|cj#SKz_Mt@4*<%+BRyjmCJwR&ae7}0;D*L7+B;tAqB-P|L2#mE-_-rnt&@T0~26~!LmL&&@5j1zs=L&^KvUE(=x`jn5!EA4lh#hmBGIx<rX(O-;xD7?CHHF-x{MRR<b^esB0B>Gh~n6<D9X5XT7vMgVrx#TZ1{eOjCKK`eDg^nHn|9*weXKPr=Di8T<a2|LCigPY<88{cb1i2Wz1iTQL3Ff&7%=2Y1&tHHSg42<6!Rg>R$mhXxz|SEkfPcwqDY6?bO)q2+_ytx^v5G~8f@8r`kiEePtOl`~%8FlZe*OC*r-G-Vhw~&>Jy=ad27^blieVMaY6Nl|G6tN&Y80!P$Z_DA;MvF+@NBRXIU208n$Bt{at3%PI1DudpJNa{XD}+kvi?ap7rnv!oFuav#>#>019pI?AqRk`ffJE~!HM8FTnm0}dLk!-dxArdao{-oYzT^TR}|-P<N$CuxIeNFxIg$=<S_8F;33Foz(c?zkv{{E1V^Aak4L70dA<l94<3u+oQ6yV^GpJ#foGwTaIKSYJ)B4f*n#uzL?(h0aqgVR$>7O2?@nYanCBEQ&q-jO6Tv(az&xjddB%fz&H(eA4(5BC@8cAt6YNA!3Q`59fcgEw?<0OcL?TClBf(E2Rq)f`;mD!j;oyGAFmONcKxAL=K=2dDLEtCA-I2lI?%)7q4{!ju6S6nB6Sxa96x;>e8Tk~rGdK|06C4PB5*Y&K*%i$9(ir9O9^*U~83pG1neW%1BgcZrqKET(Rs|@N3t6pV^&1QGEJ0eCXDO=<toF0oh~m5n#aTyjcA+?LMsY4fao&RBycNayRTSrKD9+naoL@t6-htx$I*Rj76z5$i&c8)*{vC?*8z|1@tagL<pg6yYJOJjo5Bw&0FRRt8*04H=Tnpy84$QL%d<a>LECQF~czi86tg=~Uv6{zfKC1=Dm%t0a8OUFOGr$@$3!H_S8jACB6z5lvIpDOEfWWYzANwzg$1k1VK+=C$*nd*~v&{OFNo-cfA8BbRo%y}RZkRyYtZ(t(3d(;0YNHa#'

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
