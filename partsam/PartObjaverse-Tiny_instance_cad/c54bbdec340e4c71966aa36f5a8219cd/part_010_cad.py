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

PART_NAME = 'part_010'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/c54bbdec340e4c71966aa36f5a8219cd/part_010.stl', 'relative_path': 'c54bbdec340e4c71966aa36f5a8219cd/part_010.stl', 'source_sha256': '0d3986f0cb0a3309c6dfceeb0105c5de75d825ef1ea9614c14bfcf30b40ebd94', 'input_faces': 192, 'input_vertices': 194, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.05758501589298248, -0.06541866064071655, -0.11089912056922913], [0.21309345960617065, 0.22831764817237854, 0.015604296699166298]]}
GEOMETRY_BASE85 = 'c$}q~2~ZSg8irdu5pRhH@fZ~Y8e&96G#I9h_r;F4L4pGc@k9Xy4Oc6O;t^34Q31#MMo`3yNE>4$8WS~fV>Ie$+{9gtN!F0WO^i#w-^;E{u~l2UQ#JKI{qW7#|NPVach6uMR=tL+B9C^8#qy<leiKD8p7j)0B_=Ft?zG8a(On|uEU2b5f;S!&nGrB{gyqd@N{kZcF(oW|a+JqwCXYVhy*#{39^td2=0=4?Oqv}vCCu;xLuN*YmHX(aA#=jYw>`ak_wX`x@8o4lF#V5@y5&RAO5+Zcl&3n-a^7rY{g*Xk+jKfmd}P^2hPUnvPsDb9>^`LWDZFVw?0jR}K4OOW@!inJddnrw*w#}E_8@&9p<dnN{toK(Eb+19P_Mo481-u6_q*U9))3GATGwBJR|6u&e;tv8?V~<BQ9r+#?04GHg~qma&{h21WO&o>&Wo_!EoD1icdrAy{q1YX7?1NLczx^|c>S?+im|OcxV{bb_3M6&{T{eG&)Bwo^5?Cn5Aa64?Lf7~*iJbBuO7>laTd0RS66?s1%E%@7JU?_fLM%kdM9{weH^@P;q^J_f7Vs}`)2e}2G5f|6Th_~d*sRIRpFP`gV)D(mvOeeg8pjpfn4}mneg@n$I)NE?Ja)XD4Cy%K6SsyfiKmi{|8gxwdEgX<L?g!NdM*q=&ziZu?h8^^Wd$a<Ivxfma+l$?lUX(QJ;>2*O$C0^H6uT%tM*C)Ms9oc`NQG^BL1F3;wTXQLirBJ{zBxW#T&geMFS_e|X7w)=ypwUvyjgPrMa@{{FvappVx|nNLfm^zTw6KKD1-uQ~?a)TbyNzE8TmuZsS*A6DUYJD$os49iA;Q^w5YQh!j6pWtigV~cYZpV#^V#>xGvsrOTne)%%~ig~#BgZzDk+eLVe-*o4WoF7fj%Qz$4@Otf|MDZ!T(BIDes^|O2=U?q3>E9$>`mY}wgYozEMt>zP6!WPlo)=ExIJqk4QH)>e^IpB(5B>G<CyOi954$4s+=9nLMSXH_^w;@$X%_=x%vJ1HQ+mdls~YFC*f?_)?@McbL%icWO#N=Lxr%wy+WjTfT*W-=&1x+-SM|AcnI_)hb5#7kTV<}|bJx=f)6G>JCu)3QhPjI4N?Gx<c!%RqyBD(7T*Yy#+C$cvt2oZpGi|fXRh$<}|E?R%Rh&o4@R9J2=be6ak<>e!r&{gln^5m?UMtr=$VQ#RI-pOunuB_Wbwl;)nhWo+&gjnj#XGD^rh_gvsdre%el8SW)1wsQ@AM<qXOntM{N@wzYK33)4ZPzzsZ6WB1=}r$%Jr*j6L|Z>rs5seTYLQ$;@e)3dd{bPwWoN8bzAxJGQ8tDZw(CHiuyGzFit(u593t7$q?_gAKqSVxQu`Qe(?_15vA*UTje<P!+7k@vrupU>8kjB#qfGgNoDVFol;!`x5>N($>$sBBiDt-*Wn$ncUq3icGUaU$2hH>F5!A=t<xJ`J-@kB>g{r!^|S3j{o48GFmJBIabKbByeR&2MLw^rAn~1V!K<@-%DhcC;dnO1dG3Vo@(Aatt*`4`^zRV73toTvA?laf7D%5Yc>T3mvfuR6@YaXxcccDcP3a%V^J~s-@!y@5{!aCxG0*;Y;q^^%@LKqB+3#@oJ*dCkLDr>&R+u0CU{`p(`c8~T%L$Iecrr&wePS8Bbz72nw_vHapOND;I1ByN_DSNehl+1G8{<*?B}<=NH@S~89hnBdbCuLzP~?85_%8aZ=Q5-|E>n(&aG6i-PV;@({%jJ)qjrl9fp=;JuO3g3^DCflfA}y@@i%O!*IBRTjTG;>QmzY~3S^w0juo#AhF4;K!~0U!MTk%MMb=f$TZPx3o<qHr>wwZSNxZ&Uj@!XL(r4ll@elgTdh&306ny-0>F@Cn@7HGKdZlDb{m9ku$_vq$H~r#OsV`{*uazzzkN11`*nard(`6n$+a8SVF|`k%&xs&8-n2XS{SBYlQ2gl}@r`Uvu{|_g{Foo5&*~!<q_2A(`mLTI>%ir^QP_Wv?c#Uckow2VBd~qvOYtYNrT=K}$=G(f1+O2PD94*?r%<FR^dSB|XN>e&VN1kz^V0|Ae7`Qfs5-8r${#nyXFd^sGdWP^&o95y`}%u$H0FCvUwCzIpd3GEY#6`&m3iXB9?Lqg_If1hlS-tIYnt>g$Otgz*<O0TQh&{QJpp}QE)&0Dg7|h<;$<FO3Xoqfl69k{B@O+@xQQQeN&3g0T#E5eX;mP{RZSVsgEaBZ-r@`5rQW|$5HiS5Jl89&X@ey=9!CdC|IJTi9!j?2KEpmaNb381B7H)9ai3wG8!Y~<Lo&{eWw>upe~pknW$rSb@9WF`M4d>fKc6f87i~<D_ZKboZgu6jjWbJqT$1>OV`ctt*F?R|v{w4GNW=KmjD;()pCQM^UwS6>zGb+-v2QvfeSWMV$N%|3D=_|sR|=j#-qe_{mLa#@lRo1uGS1Hj!P|U)skC4FGZ(A_rom6dFC8!Qv-hcn?SQ~TmFBtM5v(Vsj`PI-Em`L0r!>r`J>GN}zVTqx>%oubU_6iV;8o|hrBAUtj%RJ-J*jVa?kry4v%B1f2ly4jM<0f_y3N9MM~|;|1bx=U!fQWIw;Em<nSDgg<9FeeuV(n*b(i)Rq28tA8TchP)}Vg$Q+Pe1F}&^frTG3}GM_w(`l*-RNBtqWj@$bO9fPlN58m4DT^Wy)&k2m9G`j@#k^cBTru9n@pT7X!=K0e`^uO8lB>dqgr?CGOt?|7`yYi{{hbGi(sWMJ|-4N7iKDA{3lXl7X-m|O3`+tk^Dt?Rby;rN>TV5YI3*OXV6TW9EmoJO|I1Apsp~hzPSwHDCyr+Wm*fxDQeiyLqS_rRfIgj;5>)2th;nmJp#1FfT^-P;M7~k{l$*pC+p823&IoTcG=k0G4$-LkFVl&1w-m3un9r}g%Wi#QG?d$RlZ@uX80k+)|aDQsI2j!u@O_caQTH-#`wrvc4@36kpMviYKpe^dsuNGpQ%T)2|TW{d~-|~mIw$2c5=@5?k-|rkkM%)yio*Ihnw&Cz<y)|+^%q_!wY3b{aVSc=d#6M6mzuHX&-gLTDeBnFt`$2B6qsVJ6vMyXrl-~&^<riUG*Xqf2H}B3t^tn5^7<s>ec<WZoi(YH@No1Yw;@i2wmtVl)wH*V+4=RCI+q;}Bu~hoC>yMnwYnpR;Y5CJxaaF=Yp8KiGkjA4TtNy8LT95zor><`Q?@wLz%E!>K{Mm@vl-!8y%4|+{CAVO@kz0^kF<X;ck=roak=u~lGdq&olV4(XBELlL%zTC1ncRg>gI{HKCBI7U&g?<%PWEN?BKwm4n0?58<ky*I^6TWj%s0q=$pe@J$pgqEm;q!X$B{>n$1;P+W62YlR`Nvhr1Iw+<}9X_Jc}H`3?WC5XEQ^|v&oUnFmfb0iWyFhB1bc)lB3CUnbXK~$@7?RlZ~7~HZq1hkGz2S4tW7Nj+sa{GKm~V)|km;jhw<<MouATF*lO4$hpkT<XrMr<~H(H@=oS1@=o$z=05UXavt*_IgfmZd6;~NT*N#|E+U^`o+O_jpJM9dQ{)onX>tj<nE4*Ln0$<RoNVL~@-cEDvw&Pk&SxGV=acs{_mKCKcQbd8cayg>w~)7!ZOk09jhxNgM9wB}V6G!?Ag^SuCa)wfWxh*ZN?yWTMP5QqV`h-k$jg~)$;-(rn3?1i<aFkGvXN`Z>Ey-CRPti-Lgpg!LUKGafgDes&x|F{C(mR~CmT7LJd-?y`4)K!Ihgq-IhY*C98V4;PhkFuJb`Rs4k8;lm~0`BVh$ybB9CScCyyqNVGbjYA&=zK;33TZ<RRpKOqJY^?9Y6S>`(5^>`CrT_F;A-`;fhvFO$8=UVIwt$@Cz5lHHjd$nInlvn|;~ev#Rd{35v-^96D<aua4_auad`W_@x4vJ0~=*~mI%7qT<67TK9xn^}Wgn_QFWM6OA$&a6hRPBtEvVbz>mtN*8eRsQ>-;RVnC<I?e!m2dl=f90d{UjMoYv<$0hjJ<q7PPmZnG47C*e*zHU$2b'

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
