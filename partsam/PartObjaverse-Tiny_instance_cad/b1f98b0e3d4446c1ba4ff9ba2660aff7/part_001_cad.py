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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b1f98b0e3d4446c1ba4ff9ba2660aff7/part_001.stl', 'relative_path': 'b1f98b0e3d4446c1ba4ff9ba2660aff7/part_001.stl', 'source_sha256': '9babfbf446f0d95fecd6b9f1a84f452b830ec9dd6facdea9911ca5cc8b0e1384', 'input_faces': 250, 'input_vertices': 187, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3508553206920624, 0.2836705148220062, -0.38434916734695435], [0.2551684081554413, 0.33841603994369507, 0.059272781014442444]]}
GEOMETRY_BASE85 = 'c$}q~d2CeI6^E}`3>X4|I2%hCmevr=YQTmBJgwOc#w09;LKtI@i@^nB8wv@K2RN7(C+ub`Fu?|6Fk2E*X#U8wIF%}eH69>Qs}7Nhnl5UjHf;iJ)OY88_vO9IRI1vMj((qi9G`cW^WM82a<f~uN*3zVOSHaxCAn=EA!KwA$zoNotfIIeSUzZ3>6!%bXv~)%t-Eq&P0O8|AXbT2QVN6R1!XCteJRfuWu&C~Qi_(BRg~o~Te!TeFev>A`6cB++b>_7UmCQ3?l&|eJ=K@iKh?L+_dkA;>>)&pD{j4SYxv-aNT#jUk=b?fXDh8d=39S19P@n*7n<CD7~isX)ykiJ|5~B)+iZ;a(GFLe+<pjOd_FXmAO2;j^0{u{Zl$V!WudCSx}Cc2FMfX6?MLyg9tHKW`X6R1e_U0wJ74?0@ygfvq3Ses-M{_mBlkG9AI8`73Rez^`GKc`vFnDePQ2{)Eqv>bQySd9o|l>LtTXx6pgyYpZ#I79nJ>PDugC8n*h$rI5T1PPhw*iOH0|q1y!F(+xt=2Rfy#e>$4&S8XkUbtZ~aB>qv-o(%=dr2Jm&kxA8K;@0eq{|7vB8ZH8<UT<>ccF*5BIuStQ>6YTw-7=vQHtf40iAKH3-Osyypsec7n$tZnUGe|$f_&JVONiuu-})vC`IG+cK3A$+T`$&;`9!OVC1fqY-rJT?B}$+30tAIiGr_N~qNYCU~DZ+rZe>y`h=rxCXw#&_;V!`JJteX(l2XTKiu*>}?y_x99ey2sOXi^^})(>wk@SF8N1p^!U2RCrMNtIvDp<x3B#I!n_%bwV57R{8gD)Vb^Ub^k{a?|9ZTCn@HOyl(aGd|yh9%3nIblkdBKK;<X;Pk81vWkhpazx(Lscy*#*e4zX}-s}1gTx*UuPI0-r>W8nq^Af)u9*MUO*7;G9xa&42OXXiN*7?EINW6XVU7Zn$*FOP#vwtj|ub=<AKEC*!w;w{=$|LdmHvIACh`Y}NYX^Jo7kxi!-??9^6V&~3caZ0Pbe{kC&i$zKH$CI&|4`|@Cb$1kpW{3Itk*~9ciZCafBX>7PiLLAzq3Z=kIf9Z^L@W=Q1|<&0iJx{%!{hdCmrkD`GH=YRNrRg9rx6sZ>@W4>)pQYThrJ5DU3SS=TEAAG_ET~4~WDYr+7>Cp*6-kuh8r)Z@=kr_MhbKH$5+Wr{DB=biVF4T_0cfo0XNQ>YPYX>zOcLy+`q*O_^%_yUxGu_Qj-4H{JK6_WiB?q3Z0d@c8<<;UBo)<Ll>u=?5}DZjM*SxgU+|hSzV8#2aUT{@3&JpSsu_^QR5H8Q0%CPWiu|e%tLk{akzB<A-lOQ2A-|@3?(EU-2u;<LmjFzB6C5j^0P(y8gzkk$B_ubI#QB^7S0yov(gB;_LUORhfR<?F-&J;ml7xzBAuzS$EvNv%kT`9^ctt!w;7<H^-}E(f<!!m*<{2PG`Q%ON0i082f$ZYXz<!b^B3#(YO1)OqU;6!aBT{UF-Hktb?`Z&Di_Pe{tj$cYSeVS**VHo%#hw_q+3>^p$=tX<t7NtqX+>Za;8at+N=mqS5V#bYI=wbJ|m<2YqGuQToanYShus0pq%1`brq%)PKK-MQUE+vm46ixuMtLA-}+zANYXh$&%7Kw{P)05s{RWZa>QN#F{buwA<I~V2QbB+`e81)7R@Dj5@x5@;qtwUf2JsdY)Lt-f`;psk07?TU?E)@gCH^`99LV`95;;jrWoE&G(V^&G(U$Z@iBj-*_+hYgWd5zwUp=uYG-A==(+cqDq~s#ZR^z_4vj*n7)4RYu`NIIzI1xvyLywxtDXP_RaIH_M@C{bzeEYalUox==<xhfAHj+=UZo-#`)Hnuf89RI_CM-@%8z(**i}2eCzo7{9x2E&#}%pjq|57U*r7g)Y;DY^PqQs&F>|g{`o{bpG6<~<m82GvHmgsJ`G=bFXo$n7l+0?aXof_8Q&*FPtUym&~<Y?-y#)MPQ01X!M+3RXeW|IQNHUdBx%Zz*7#o`6%YTfzCs!{V#xpd71CaL%h<6GJqYiE_oD~kXY6=X?guJ=?u_<?JHwBmz2L{-E~pRIwIs`BOthmrDt~T+J`T5m+o3(+c5qv?JFII-e#DMWvMtbW!F}M#=tOujJPDluPl9_>N7n6#c7Qv=ebL@<Z+^EgbCz>YV*G94B)BD-2q&Pe(L^|rb!kns5#M|yw;&|9LfgTu;Pz+|oW$7Lqn+W->}7jG@{@$*ZiM8g(Jt`Q@Kc23u7u<#&?H#)l~1TXlG+PSW?vsid%*qec-B?(S*{~>fa|&g7>m?YIF)frmisRExDR{Uhdt~7_eLkd-?77Q$M*=y^UzFq9y}L)9-a%&L5IR~;9PVNoD1im{oovUsvT3%{%AjVz8wqf_%0zii;z4P&4b6n&!My7=ipK3EO->0j?RSB;gRTz@JM(#`T{&09)`|<hrxr<>F{89AUX|}nhj^O#{*fz9M?MMun$w%zp3avcpm>g70rQ*>?pM(h%SeNa3Q)3E`$s0D7Isv9ZS#vyaZl~=EF<j5_Az<0{;LlfD5>m<R7A|(Pi*zcn!K7UIV|3mclQ?uMm<~phfTs`1^K@N5`Q>@Hlu38idEdqtQZmG@OAJz!~rebP+rPPDAtIG<XOafQP^-=t4LJ{x%``CA1iR30`bR8Cs4O!{u-Vx&*F(SE5VdmGCOG1TJC!R=M_7vb?Wle@}y@E<mTl3*bC-2Al`aMqhwu!?VyAVW~6W8awLjI7CQ(%Z>}^&j`tv2+0@GI`|^|Q$q5aXbrsEj$L-VLr6Y{?u5_5XV4w+8MqPM4mZLL=r*_ku1DX1>)~VQ>+mr+WXBP-8hstEhBpwBH==LA8{tjpHh2?UiEf80;n&a|@N4j9bSJzSu0nUgRqz&cH@pS@ksUuq_n^DsJ@C8eJMg>k+l1uv=sEa2d=@<epM_7Ojqqvs6xslvf={CL@JaXtdJH}RA4fy*ak$pCm$iiCqeAtf)Whfz_%OT`t%j@F@2!Mn%Z|0^I&=fP4qlILgxABb+L4=`&?33zfBLWMZ$6ehFnazY+x$)MpDXU)oM6{-{&>mFZY|H4_93!G>;ZpCp3KC*0ccm;wE'

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
