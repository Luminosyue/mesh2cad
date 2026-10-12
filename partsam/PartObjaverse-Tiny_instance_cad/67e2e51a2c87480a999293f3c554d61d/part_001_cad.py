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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/67e2e51a2c87480a999293f3c554d61d/part_001.stl', 'relative_path': '67e2e51a2c87480a999293f3c554d61d/part_001.stl', 'source_sha256': 'a8edb45a4dd2af910a8fe27aaaa5339fccde5364dc7c02488c06b3c9ab9e7216', 'input_faces': 248, 'input_vertices': 168, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.20713035762310028, -0.3995899260044098, -0.153994619846344], [0.2155461609363556, 0.0223962664604187, 0.3737880289554596]]}
GEOMETRY_BASE85 = 'c$}q~3v^9q8iqGQk|ruh2||w+ks|Jq!LTE7sT66&J?ca*f*_J0MfC(Bk%)wd1mTGLt%JHm-L^_dNT=>~cdARPN@=Su)s8v;`@Py^*34S7X3kpQdY}EC|9t!3-~Rsp?3@G#RdI0F<keU!3XH0wyJ?yVSIu3U8X1=`Has%kXJYIJl{7c_>h)5W^dHnOcvvNEsy4$bA~HTa&a1P@t80{>S4)#u)TFqCxUh+%CdEZWD!*4)Onju>kB<(EjkF&(Z|m#V($wC&rRhV{|M+^vJ_U34IVX>(xkO)>3hnu9V|TmQqOX+V*r^MA%lI#j!1o?1e#)J6b*#nyzFDbp_d*H$9o8vI4O33B@=axj#4qf)uzR^Y=B8;S70&BAD-CMa#ee#KHu8s_*^19SFF64}cM|gGWdkLDr;XxgCTEw=Zy6DPqQX3FduQP~4m1=$xEkiErv;wE`~HWH!=GCq=S{4M{I>X*;}zy(NiyTuqlx&&L77j|v6HAn^k>EJo2N+K7G2tk^K5P*zGtb-v$~G)wr8b9@J~O-JT3FT-l&dEw=%>pX_TPUd|=LLT<`lAkHNP_OCH}=>(sF|Z@2g<Z89+K>YEsEesKLW_}d;}yq=!?1+HUD*Q4<DPVq`@Z6eQM{1<J-zjR;jqo3Pe96w7jpncX!{>*RAV!UGv{ZOfc?eHhax4)YB##x!?!b+c@K8OB(MDF)DQqLJzaliCu+r-cIUW&TB9)<k+o&MtcEy8$XL-J0{tMS#t@I#(So@O_X;r-#=#DD0Fd1@}#ab8PbXYn(oK7X9od+MR`_eGnzV<pCWH4)!5M8*fKM}95y_k(i1budpO?7|7C&yfT0H$6rjw4%pW_<cjgFZ>XBEG3~BudVYI-xv^w`>n-a!1&l2pTc+ZScLlO*UsZ}8UNT1ziWFrZ-<}Ix5mn^_Lr}-rnd`3{Wm-*gr5+O@uuWH$YY+jQ2aY5F(18tSLuJx(S;T2<}@G?`JX@8Cw(I8#j@^O%-d*dlfLjcE!TVOJ<LO2|8$S^^Dw!Oa~!2_mmb?wq5p@M;q%6K$978|xn8|fed*7|YvEhYOqBg#^O=va4oZi~_#M*ETCH8nWL|H4B7GYm^MB;D2>CPL-UUC`e=<J5<?cnif4LBSq(xh#J_TWCFt3RV#lMt>`PjM!V!Zy-l^yVZ+aT9<&MNn7dYf(V*SW&Cd|wai(Z~qhQvSYcQ7)@dpPHTEn;m~RgZKN7*reXKmR#P1<J(=tk9cbi&QmpJqpbHG$Zx(pOV-7j)b$n4`%3`&Mt6!RfS))H=QZ-DppW%~!QwyMg7t3k_Qd)$Yz<bSUmCTzg!i32QD<YMPd@x&<23xZ-B~zpm$w4>KA3$Ld46-*gY*AwHhg=*WIoR6n{oW(=DhO#rrk(EeY6+p;zu7t|6AxAWj`#1Zz-FE^L_vAm#ELDW5hQ+Gf@|3U-;&cpJ&5w`AF)MH4pd8c;&}*_$hbcTWw9TziD+3$KrgeL(o_Hfo{^r6Y9X%??+z5`^A3JueA<M68%-`GpM=rUrL*?O08clzKr85mp90|4Ua&cWviubwY25XHr0G_e#<VY+rjbsFwZWxa!{`~i)H-9%ZpKmy3Lnie7=vIcjqy=FTYgEg&*AnpELK8>oPW+T7f)Ik|qDf1G~{DGoE8V(?b0*-ui2b^z$zx^5JL4qn_3tol#F?;A8P^uT8-9HMuAL;N`2tmvx~nnIiYA_dfC6q9@D!iIwl8eI2ZF-hAnYLy71ITTspQ@Pi{IPt!5zPg_nC@%!vS9@Bky^r!WO8=gmu9=fcH=)4ax-{MA_%I7y`c0~VM+y5ZG79`i(BMIxpbYe7~Q>=kMOP+f^$ZIlU;cMyMsqi~jM;?>sscrCw-jjLy9mYB_kGUbfX(ReYTfAF*r_~?B&;4AkH{|EF=!3g+cEZ<ZU_Q2j0@*iiG}s0I;TXA(MKfjpan;37+%A0{*jM(ewKw5g9B0dZIAVb8N8Oz8{ia!;jYA!GK9v5CZHN1BocvCn*Xp~L;`rnD;A=&)j<nq!GH@S5Ld7@By3=ABi+?T^>svejJFZK6ryKTLqeIEw^4Db@UIY8QcGzW~)Kk`-<;6BxU&~q-O5JM9d86CQ_ty5|`*CczqMpXhVtl{o&631V2*Z8RbGFF-es_WRT0hBiCu=%1Gh2M?vWZ8^`Ie-e;?LZQd78Wi;CoOHD*Y6G;dSIOy>lDB@$jtpcjjWe5#&&YJe8adz>kr2XJ7DcSZ7au6yKPJ{lM%p^MV}P4niM|m3jUgum*bN#v$l$`T~63W3N27UAQHFdWP%=+wb5xLEoBo7`}t_vo<S4)@NQnJilmxdr%*vp|3noOf5T7A<xxEcy6)zcQBA|$!+PM*n899clCp>#g=e?h{bxb-0dyCyAOQ5>u~vAycS`Uua70J3XV;i(#2mnS^Tip^1Qd{y7(mt(ub*gaX)PLzZZYguTuZ2KjFNZr`u8S2gBE0vvA+_s~g03%Zx^y^~tjDrQQ_Zv;+H<_WUOHZR@26;?L|U>-xn}`Tkop<1_dk1Lq-cpM=kmr(b|P-xXe!>vgx{ImDFHut?T*-7M5+e_QmqwJf%%{Pk*qhq2yG4PJ<!xoHg6WBbK2etvkdth);-m`Cs>d>`7XMT>uaEw0y+oq+Fq>-Od1yFQToFGA(-i`;|aXZN3v`5%8O&%OS4ip%$d#eds&)TzO^<FYP#jmLQ(kHX(0M)Fee0~_PIv}?DJ-}L1!@m>33o|Xa|_8rsFYvMm$fVvsG=16@uyb%A|8kwhg(7Sj)sr`ux^FP-H^Rq_gh#x!x^)c#4;`!5Rb}5m5JI{5!ZaV6@yNUSb+tOD(ozOSd_5LLl<{z3M*WdV*_#S8Fyc33EzqYPuQ7Y@Q2<ucUl6}SeZMV`2d8Rufzxm7{@!PzLdFr?KA-_4~w)nvgGCm}A3-Z@-ME&d&lzuy1YXatLj22&)>$QCCBJ*D|PyB>=xQ|-T`{*0fRS$U{xAj1uYiBa>eWp7s6aQMi+?Ro~cXbc0@aw~hRnHPluJ#o6aMs+lsIYQBJt$MXUh2R9>0xY#|LUiQb{+ojpB_4@(%Qp^`WD%T>_u%t_9DN*P~4E(n5^`5azk=`Y9n%eay{ys<a%TiwFTKkZq88Lj@q8A^e^OgWIu-D0BRsPfINiSldN<oS?Or<5ONrGJUNU!jv7xMM~<U@Kvp`F97mqUP`r?#IF~wyoJ(FsolRavUP+xrUP;cQ&LHQJv#3+aS>!b81acbLLX9L_$O+W<$qD2L>U-n}atK3lAL`p=rCrH=$epMi$(_jF48;woKI8^ucd8dz=^JEsat(%J7ivSY()wf<vJ*pbHEKO_HL@$!L{{3I>`JahZAY#}_GBn-P4y!y4IsBB|COP57<C9)X&8AJIh;C<98Qj*#*vjyBP(4<jv*&86whNQ&ZOp&Gs!EctH>+J1=N+~0<x8wN4AplsafQF@=|IVc_}%aY9XhSlc@>hWbzbh1bGTMiW)+WA`fCH?oI7OR@#Z&o9s*VCi{|`Q5%q(k?S%P*QUCYmDV8FCReArkgJm&sZL}^vIDgm*@0Y{>PoImcBa-MJCoh0o@6(&2SafyYHPC6zmi*#yD=1xqz)sGBu}J<la<Dhl_rrVk|$B;kw;Ktsq@IO<P>TqIfb0fP`sMDf~>TFyqdg$p?DqDN?u1^L(L~ET}oa<Ud~XQK}{zsO(tiM=ToPU=aUnuQRGB&G<6U;nmm}=n>?7@i|R}6Mee{*+?3jkth6q<Dfu;q;+oXjWTn-~HOa3q6jz}-l9f7;tB@-(6l>JV+Mh4QRjJNorEcV^<X5R4<X6dcsIAC#$StYe$Suj;sj82MQzw#@P9neTQN`=+kz<d=_Si^P-U6!fmzDE!IBpSjEqM_+mAZtSN}g<w>Gm+&<3s9X@??%ttlQ%qdjv5QzspeEkE)XgQU@>;_h2aQOx4Mq$z7;H<St}?hT{GV#lZ~4q11QDq2y82e&m<)8^!!8Z(D}qzSREY{yaxthT<{QQ1Te^N7PZ|kH~YW1IcsAW2pnk!9kTOyI1*7|JwZXWl;@Y;UAs<`pJramX!bGEPJj${zwT9s;c&T`(mh!8-7{s)Y?A*4t)Ap'

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
